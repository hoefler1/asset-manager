"""Berechnung der voraussichtlichen Steuer beim Verkauf aller Positionen.

Grundlage sind die ``unrealizedGains`` (nicht realisierte Gewinne/Verluste) aus
der Antwort des Parqet-Endpunkts ``POST /performance``.

Berücksichtigt werden ausschließlich:

* **Aktien** – voll steuerpflichtiger Kursgewinn.
* **Aktien-ETFs** – mit 30 % Teilfreistellung (nur 70 % des Gewinns sind
  steuerpflichtig, § 20 InvStG).

Alle anderen Positionen (Krypto, Anleihen, Rohstoffe, Misch-/Immobilienfonds
usw.) werden bewusst ignoriert, weil ihre steuerliche Behandlung abweicht.

Steuerlogik (deutsche Abgeltungsteuer):

* 25 % Kapitalertragsteuer
* + 5,5 % Solidaritätszuschlag auf die Kapitalertragsteuer
* optional Kirchensteuer (8 % / 9 %); diese ist als Sonderausgabe abziehbar,
  daher wird die exakte Formel ``KESt = e * 0,25 / (1 + 0,25 * ks)`` genutzt.
* Der Sparer-Pauschbetrag (Standard: 1.000 € ledig / 2.000 € zusammen
  veranlagt) mindert die Bemessungsgrundlage.

Vereinfachung: Verluste werden je Verlustverrechnungstopf (Aktien vs. Sonstige)
verrechnet und bei negativem Saldo auf 0 gesetzt. Die Sonderregel, dass
Verluste aus dem allgemeinen Topf auch Aktiengewinne mindern dürfen, wird nicht
abgebildet – für eine Schätzung beim Komplettverkauf ist das i. d. R.
unerheblich. Keine Steuerberatung.
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

from models import PerformanceHolding, PerformanceResponse


class AssetKind(Enum):
    """Für die Steuer relevante Einordnung einer Position."""

    STOCK = "Aktie"
    EQUITY_ETF = "Aktien-ETF"
    OTHER = "Sonstiges (ignoriert)"


# Die Performance-Antwort liefert nur ``asset.type`` (``security`` / ``crypto``)
# – der Untertyp Aktie vs. ETF steckt nicht in den Daten. Daher wird ein ETF
# heuristisch am Namen erkannt (alle enthalten "ETF" bzw. "UCITS").
_ETF_NAME_PATTERN = re.compile(r"\b(etf|ucits)\b", re.IGNORECASE)


@dataclass
class TaxSettings:
    """Steuer-Parameter. Standardwerte: ledig, keine Kirchensteuer."""

    kapitalertragsteuer: float = 0.25
    solidaritaetszuschlag: float = 0.055
    kirchensteuer: float = 0.0  # 0.08 (BW/BY), 0.09 (übrige Länder) oder 0.0
    teilfreistellung_etf: float = 0.30
    sparerpauschbetrag: float = 1000.0
    # gainNet (nach Gebühren) statt gainGross als Bemessungsgrundlage nutzen.
    use_net_gains: bool = False
    # Bereits verkaufte Positionen (isSold) ignorieren – sie sind keine
    # "aktuelle Position" mehr und ihr Gewinn ist bereits realisiert.
    ignore_sold: bool = True
    # Optionaler Override: Identifier -> AssetKind, um die automatische
    # Einordnung zu korrigieren (z. B. einen Nicht-Aktien-ETF auszuschließen).
    overrides: dict[str, AssetKind] = field(default_factory=dict)


def classify(holding: PerformanceHolding, settings: TaxSettings) -> AssetKind:
    """Ordnet ein Holding als Aktie, Aktien-ETF oder Sonstiges ein.

    Grundlage: ``asset.type`` (nur ``security`` ist steuerlich relevant) und der
    Name (ETF-Erkennung). Krypto & Co. fallen unter ``OTHER`` und werden
    ignoriert.
    """
    identifier = holding.identifier
    if identifier and identifier in settings.overrides:
        return settings.overrides[identifier]

    asset_type = (holding.asset_type or "").strip().lower()
    if asset_type != "security":
        # crypto, cash, commodity, ... -> nicht berücksichtigt
        return AssetKind.OTHER

    if _ETF_NAME_PATTERN.search(holding.name or ""):
        # Annahme laut Aufgabenstellung: (Aktien-)ETF mit 30 % Teilfreistellung.
        return AssetKind.EQUITY_ETF
    # Verbleibende Wertpapiere werden als Aktie behandelt.
    return AssetKind.STOCK


@dataclass
class PositionTax:
    """Ergebnis pro Position (für den Bericht)."""

    identifier: Optional[str]
    name: str
    kind: AssetKind
    gain: float          # nicht realisierter Gewinn/Verlust (brutto)
    taxable_gain: float  # steuerpflichtiger Anteil (bei ETF nach Teilfreistellung)


@dataclass
class TaxResult:
    positions: list[PositionTax] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    stock_gain_gross: float = 0.0
    etf_gain_gross: float = 0.0
    etf_gain_taxable: float = 0.0  # nach 30 % Teilfreistellung

    taxable_before_allowance: float = 0.0
    allowance_applied: float = 0.0
    taxable_income: float = 0.0

    kapitalertragsteuer: float = 0.0
    solidaritaetszuschlag: float = 0.0
    kirchensteuer: float = 0.0
    total_tax: float = 0.0

    @property
    def net_proceeds_gain(self) -> float:
        """Gewinn nach Steuern (bezogen auf Aktien + Aktien-ETFs)."""
        return (self.stock_gain_gross + self.etf_gain_gross) - self.total_tax


def _abgeltungsteuer(base: float, settings: TaxSettings) -> tuple[float, float, float]:
    """Kapitalertragsteuer, Soli und Kirchensteuer auf die Bemessungsgrundlage.

    Kirchensteuer ist abziehbar, daher die reduzierte KESt-Formel.
    """
    if base <= 0:
        return 0.0, 0.0, 0.0
    ks = settings.kirchensteuer
    kest = base * settings.kapitalertragsteuer / (1 + settings.kapitalertragsteuer * ks)
    soli = kest * settings.solidaritaetszuschlag
    church = kest * ks
    return kest, soli, church


def calculate_tax(
    response: PerformanceResponse, settings: Optional[TaxSettings] = None
) -> TaxResult:
    """Berechnet die voraussichtliche Steuer beim Verkauf aller Positionen."""
    settings = settings or TaxSettings()
    result = TaxResult()

    for holding in response.holdings:
        if settings.ignore_sold and holding.is_sold:
            continue

        kind = classify(holding, settings)
        gain = holding.gain(settings.use_net_gains)

        if kind is AssetKind.STOCK:
            taxable = gain
            result.stock_gain_gross += gain
        elif kind is AssetKind.EQUITY_ETF:
            taxable = gain * (1 - settings.teilfreistellung_etf)
            result.etf_gain_gross += gain
            result.etf_gain_taxable += taxable
        else:
            taxable = 0.0

        result.positions.append(
            PositionTax(
                identifier=holding.identifier,
                name=holding.name,
                kind=kind,
                gain=gain,
                taxable_gain=taxable,
            )
        )

    # Verlustverrechnung je Topf, negativer Saldo -> 0 (Verlustvortrag).
    stock_pot = max(0.0, result.stock_gain_gross)
    etf_pot = max(0.0, result.etf_gain_taxable)

    result.taxable_before_allowance = stock_pot + etf_pot
    result.allowance_applied = min(
        result.taxable_before_allowance, settings.sparerpauschbetrag
    )
    result.taxable_income = result.taxable_before_allowance - result.allowance_applied

    kest, soli, church = _abgeltungsteuer(result.taxable_income, settings)
    result.kapitalertragsteuer = kest
    result.solidaritaetszuschlag = soli
    result.kirchensteuer = church
    result.total_tax = kest + soli + church

    return result


def _eur(value: float) -> str:
    return f"{value:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")


def format_report(result: TaxResult, settings: TaxSettings) -> str:
    lines: list[str] = []
    lines.append("=" * 64)
    lines.append("Steuer beim Verkauf aller Positionen (Schätzung)")
    lines.append("=" * 64)

    relevant = [p for p in result.positions if p.kind is not AssetKind.OTHER]
    if relevant:
        lines.append("")
        lines.append("Positionen (Aktien & Aktien-ETFs):")
        for p in sorted(relevant, key=lambda x: x.gain, reverse=True):
            lines.append(
                f"  {p.name[:38]:<38} {p.kind.value:<12} "
                f"Gewinn: {_eur(p.gain):>15}  "
                f"steuerpfl.: {_eur(p.taxable_gain):>15}"
            )

    lines.append("")
    lines.append(f"Aktiengewinne (brutto):          {_eur(result.stock_gain_gross):>15}")
    lines.append(f"Aktien-ETF-Gewinne (brutto):     {_eur(result.etf_gain_gross):>15}")
    lines.append(
        f"davon steuerpflichtig (70 %):    {_eur(result.etf_gain_taxable):>15}"
    )
    lines.append("-" * 64)
    lines.append(
        f"Bemessungsgrundlage vor Freibetrag: {_eur(result.taxable_before_allowance):>12}"
    )
    lines.append(
        f"Sparer-Pauschbetrag:             {_eur(-result.allowance_applied):>15}"
    )
    lines.append(f"Steuerpflichtiger Ertrag:        {_eur(result.taxable_income):>15}")
    lines.append("-" * 64)
    lines.append(f"Kapitalertragsteuer (25 %):      {_eur(result.kapitalertragsteuer):>15}")
    lines.append(f"Solidaritätszuschlag (5,5 %):    {_eur(result.solidaritaetszuschlag):>15}")
    if settings.kirchensteuer > 0:
        lines.append(
            f"Kirchensteuer ({settings.kirchensteuer * 100:.0f} %):"
            f"{_eur(result.kirchensteuer):>25}"
        )
    lines.append("=" * 64)
    lines.append(f"Steuerlast gesamt:               {_eur(result.total_tax):>15}")
    lines.append("=" * 64)

    if result.warnings:
        lines.append("")
        lines.append("Hinweise:")
        for w in result.warnings:
            lines.append(f"  ! {w}")

    lines.append("")
    lines.append(
        "Hinweis: unverbindliche Schätzung, keine Steuerberatung. "
        "Verlustverrechnungstöpfe vereinfacht."
    )
    return "\n".join(lines)


def load_json(path: Path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    # Umlaute und € auch auf Windows-Konsolen korrekt ausgeben.
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    if len(sys.argv) < 2:
        print("Verwendung: python tax.py <performance.json> [kirchensteuer 0|8|9]")
        return

    performance_path = Path(sys.argv[1])
    if not performance_path.exists():
        print(f"Fehler: Datei nicht gefunden: {performance_path}")
        return

    settings = TaxSettings()
    if len(sys.argv) >= 3:
        try:
            settings.kirchensteuer = float(sys.argv[2]) / 100.0
        except ValueError:
            print(f"Ungültiger Kirchensteuersatz: {sys.argv[2]!r}")
            return

    data = load_json(performance_path)
    response = PerformanceResponse.from_dict(data)
    result = calculate_tax(response, settings)
    print(format_report(result, settings))


if __name__ == "__main__":
    main()
