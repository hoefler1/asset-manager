"""Datenmodell für die Parqet-Aktivitäten-Antwort.

Bildet die JSON-Struktur einer Aktivitäten-Abfrage als Dataclasses ab und
bietet mit ``from_dict`` eine Möglichkeit, rohe ``dict``-Daten einzulesen.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class Interval:
    from_: Optional[str] = None
    to: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Interval":
        return cls(from_=data.get("from"), to=data.get("to"))


@dataclass
class Asset:
    identifier: Optional[str] = None
    assetType: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Asset":
        return cls(
            identifier=data.get("identifier"),
            assetType=data.get("assetType"),
        )


@dataclass
class Activity:
    _id: Optional[str] = None
    datetime: Optional[str] = None
    portfolio: Optional[str] = None
    user: Optional[str] = None
    currency: Optional[str] = None
    holding: Optional[str] = None
    holdingAssetType: Optional[str] = None
    type: Optional[str] = None
    shares: Optional[float] = None
    price: Optional[float] = None
    amount: Optional[float] = None
    tax: Optional[float] = None
    fee: Optional[float] = None
    hashedAccountNumber: Optional[str] = None
    subAccountId: Optional[str] = None
    amountNet: Optional[float] = None
    isin: Optional[str] = None
    wkn: Optional[str] = None
    asset: Optional[Asset] = None
    broker: Optional[str] = None
    identifiers: dict[str, Any] = field(default_factory=dict)
    source: Optional[str] = None
    modified: Optional[str] = None
    allowDuplicate: Optional[bool] = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Activity":
        asset = data.get("asset")
        return cls(
            _id=data.get("_id"),
            datetime=data.get("datetime"),
            portfolio=data.get("portfolio"),
            user=data.get("user"),
            currency=data.get("currency"),
            holding=data.get("holding"),
            holdingAssetType=data.get("holdingAssetType"),
            type=data.get("type"),
            shares=data.get("shares"),
            price=data.get("price"),
            amount=data.get("amount"),
            tax=data.get("tax"),
            fee=data.get("fee"),
            hashedAccountNumber=data.get("hashedAccountNumber"),
            subAccountId=data.get("subAccountId"),
            amountNet=data.get("amountNet"),
            isin=data.get("isin"),
            wkn=data.get("wkn"),
            asset=Asset.from_dict(asset) if isinstance(asset, dict) else None,
            broker=data.get("broker"),
            identifiers=data.get("identifiers") or {},
            source=data.get("source"),
            modified=data.get("modified"),
            allowDuplicate=data.get("allowDuplicate"),
        )


@dataclass
class RelatedEventId:
    eventId: Optional[str] = None
    fromISIN: Optional[str] = None
    toISIN: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RelatedEventId":
        return cls(
            eventId=data.get("eventId"),
            fromISIN=data.get("fromISIN"),
            toISIN=data.get("toISIN"),
        )


@dataclass
class RelatedEvent:
    _id: Optional[RelatedEventId] = None
    type: Optional[str] = None
    announcementURL: Optional[str] = None
    title: Optional[str] = None
    message: Optional[str] = None
    datetime: Optional[str] = None
    fromShares: Optional[float] = None
    toShares: Optional[float] = None
    historicalQuoteAdjustment: Optional[float] = None
    portfolio: Optional[str] = None
    holding: Optional[str] = None
    asset: Optional[Asset] = None
    user: Optional[str] = None
    holdingAssetType: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RelatedEvent":
        _id = data.get("_id")
        asset = data.get("asset")
        return cls(
            _id=RelatedEventId.from_dict(_id) if isinstance(_id, dict) else None,
            type=data.get("type"),
            announcementURL=data.get("announcementURL"),
            title=data.get("title"),
            message=data.get("message"),
            datetime=data.get("datetime"),
            fromShares=data.get("fromShares"),
            toShares=data.get("toShares"),
            historicalQuoteAdjustment=data.get("historicalQuoteAdjustment"),
            portfolio=data.get("portfolio"),
            holding=data.get("holding"),
            asset=Asset.from_dict(asset) if isinstance(asset, dict) else None,
            user=data.get("user"),
            holdingAssetType=data.get("holdingAssetType"),
        )


@dataclass
class AssetClass:
    class_: Optional[str] = None
    share: Optional[float] = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AssetClass":
        return cls(class_=data.get("class"), share=data.get("share"))


@dataclass
class Symbol:
    exchange: Optional[str] = None
    symbol: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Symbol":
        return cls(exchange=data.get("exchange"), symbol=data.get("symbol"))


@dataclass
class Sector:
    share: Optional[float] = None
    id: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Sector":
        return cls(share=data.get("share"), id=data.get("id"))


@dataclass
class SecurityInfo:
    symbols: list[Symbol] = field(default_factory=list)
    website: Optional[str] = None
    factsheet: Optional[str] = None
    type: Optional[str] = None
    wkn: Optional[str] = None
    isin: Optional[str] = None
    ipoDate: Optional[str] = None
    etfDomicile: Optional[str] = None
    etfCompany: Optional[str] = None
    hasDividends: Optional[bool] = None
    sectors: list[Sector] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SecurityInfo":
        return cls(
            symbols=[
                Symbol.from_dict(s)
                for s in data.get("symbols", [])
                if isinstance(s, dict)
            ],
            website=data.get("website"),
            factsheet=data.get("factsheet"),
            type=data.get("type"),
            wkn=data.get("wkn"),
            isin=data.get("isin"),
            ipoDate=data.get("ipoDate"),
            etfDomicile=data.get("etfDomicile"),
            etfCompany=data.get("etfCompany"),
            hasDividends=data.get("hasDividends"),
            sectors=[
                Sector.from_dict(s)
                for s in data.get("sectors", [])
                if isinstance(s, dict)
            ],
        )


@dataclass
class CryptoInfo:
    website: Optional[str] = None
    symbol: Optional[str] = None
    technicalDocumentation: list[str] = field(default_factory=list)
    sourceCode: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CryptoInfo":
        return cls(
            website=data.get("website"),
            symbol=data.get("symbol"),
            technicalDocumentation=list(data.get("technicalDocumentation", [])),
            sourceCode=list(data.get("sourceCode", [])),
        )


@dataclass
class SharedAssetId:
    identifier: Optional[str] = None
    assetType: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SharedAssetId":
        return cls(
            identifier=data.get("identifier"),
            assetType=data.get("assetType"),
        )


@dataclass
class SharedAsset:
    _id: Optional[SharedAssetId] = None
    assetType: Optional[str] = None
    name: Optional[str] = None
    logo: Optional[str] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None
    security: Optional[SecurityInfo] = None
    crypto: Optional[CryptoInfo] = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SharedAsset":
        _id = data.get("_id")
        security = data.get("security")
        crypto = data.get("crypto")
        return cls(
            _id=SharedAssetId.from_dict(_id) if isinstance(_id, dict) else None,
            assetType=data.get("assetType"),
            name=data.get("name"),
            logo=data.get("logo"),
            createdAt=data.get("createdAt"),
            updatedAt=data.get("updatedAt"),
            security=SecurityInfo.from_dict(security) if isinstance(security, dict) else None,
            crypto=CryptoInfo.from_dict(crypto) if isinstance(crypto, dict) else None,
        )


@dataclass
class Holding:
    _id: Optional[str] = None
    portfolio: Optional[str] = None
    assetType: Optional[str] = None
    currency: Optional[str] = None
    user: Optional[str] = None
    hashedAccountNumber: Optional[str] = None
    subAccountId: Optional[str] = None
    logo: Optional[str] = None
    isSold: Optional[bool] = None
    exchange: Optional[str] = None
    nickname: Optional[str] = None
    assetProduct: Optional[str] = None
    assetClasses: list[AssetClass] = field(default_factory=list)
    asset: Optional[Asset] = None
    sharedAsset: Optional[SharedAsset] = None

    @classmethod
    def from_dict(cls, data: Any) -> "list[Holding] | Holding":
        # The holdings JSON root is a list, so support parsing a list of
        # holdings directly as well as a single holding dict.
        if isinstance(data, list):
            return [cls.from_dict(h) for h in data if isinstance(h, dict)]

        asset = data.get("asset")
        shared_asset = data.get("sharedAsset")
        return cls(
            _id=data.get("_id"),
            portfolio=data.get("portfolio"),
            assetType=data.get("assetType"),
            currency=data.get("currency"),
            user=data.get("user"),
            hashedAccountNumber=data.get("hashedAccountNumber"),
            subAccountId=data.get("subAccountId"),
            logo=data.get("logo"),
            isSold=data.get("isSold"),
            exchange=data.get("exchange"),
            nickname=data.get("nickname"),
            assetProduct=data.get("assetProduct"),
            assetClasses=[
                AssetClass.from_dict(c)
                for c in data.get("assetClasses", [])
                if isinstance(c, dict)
            ],
            asset=Asset.from_dict(asset) if isinstance(asset, dict) else None,
            sharedAsset=SharedAsset.from_dict(shared_asset) if isinstance(shared_asset, dict) else None,
        )

    @staticmethod
    def list_from_dicts(data: list[dict[str, Any]]) -> list["Holding"]:
        return [Holding.from_dict(h) for h in data if isinstance(h, dict)]


def _to_number(value: Any) -> Optional[float]:
    """Wandelt einen Wert in ``float`` um.

    Parqet liefert Geldbeträge teils als reine Zahl, teils als verschachteltes
    Objekt (z. B. ``{"amount": 123.4, "currency": "EUR"}``). Diese Hilfe deckt
    beide Fälle ab und gibt ``None`` zurück, wenn nichts Sinnvolles gefunden
    wird.
    """
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.replace(",", "."))
        except ValueError:
            return None
    if isinstance(value, dict):
        for key in ("amount", "value", "eur", "gross", "net", "total"):
            if key in value:
                nested = _to_number(value[key])
                if nested is not None:
                    return nested
    return None


@dataclass
class PerformanceAsset:
    """Das ``asset``-Objekt eines Holdings in der Performance-Antwort.

    Achtung: hier steckt nur ``type`` (``security`` / ``crypto``), ``symbol``
    und ``name`` – der Wertpapier-Untertyp (Aktie vs. ETF) ist nicht enthalten
    und muss anderweitig (z. B. über den Namen) bestimmt werden.
    """

    type: Optional[str] = None
    symbol: Optional[str] = None
    name: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PerformanceAsset":
        return cls(
            type=data.get("type"),
            symbol=data.get("symbol"),
            name=data.get("name"),
        )


@dataclass
class UnrealizedGains:
    """``performance.unrealizedGains`` – die nicht realisierten Gewinne/Verluste.

    Parqet verschachtelt die Werte unter ``inInterval``. ``gainGross`` ist der
    reine Kursgewinn, ``gainNet`` zusätzlich um Gebühren bereinigt.
    """

    gainGross: Optional[float] = None
    gainNet: Optional[float] = None
    returnGross: Optional[float] = None
    returnNet: Optional[float] = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "UnrealizedGains":
        # Werte liegen unter ``inInterval``; fällt darauf zurück, die Werte
        # direkt zu lesen, falls die Struktur einmal flacher sein sollte.
        inner = data.get("inInterval") if isinstance(data, dict) else None
        if not isinstance(inner, dict):
            inner = data if isinstance(data, dict) else {}
        return cls(
            gainGross=_to_number(inner.get("gainGross")),
            gainNet=_to_number(inner.get("gainNet")),
            returnGross=_to_number(inner.get("returnGross")),
            returnNet=_to_number(inner.get("returnNet")),
        )


@dataclass
class HoldingPosition:
    """Das ``position``-Objekt eines Holdings (Stückzahl, Werte, isSold)."""

    shares: Optional[float] = None
    purchasePrice: Optional[float] = None
    purchaseValue: Optional[float] = None
    currentPrice: Optional[float] = None
    currentValue: Optional[float] = None
    isSold: Optional[bool] = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "HoldingPosition":
        return cls(
            shares=_to_number(data.get("shares")),
            purchasePrice=_to_number(data.get("purchasePrice")),
            purchaseValue=_to_number(data.get("purchaseValue")),
            currentPrice=_to_number(data.get("currentPrice")),
            currentValue=_to_number(data.get("currentValue")),
            isSold=data.get("isSold"),
        )


@dataclass
class PerformanceHolding:
    """Ein Holding aus der ``POST /performance`` Antwort von Parqet."""

    id: Optional[str] = None
    activityCount: Optional[int] = None
    asset: Optional[PerformanceAsset] = None
    unrealizedGains: Optional[UnrealizedGains] = None
    position: Optional[HoldingPosition] = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PerformanceHolding":
        asset = data.get("asset")
        perf = data.get("performance")
        ug = perf.get("unrealizedGains") if isinstance(perf, dict) else None
        # Fallback, falls unrealizedGains einmal direkt am Holding liegt.
        if ug is None:
            ug = data.get("unrealizedGains")
        pos = data.get("position")
        return cls(
            id=data.get("id") or data.get("_id"),
            activityCount=data.get("activityCount"),
            asset=PerformanceAsset.from_dict(asset) if isinstance(asset, dict) else None,
            unrealizedGains=(
                UnrealizedGains.from_dict(ug) if isinstance(ug, dict) else None
            ),
            position=HoldingPosition.from_dict(pos) if isinstance(pos, dict) else None,
        )

    def gain(self, use_net: bool = False) -> float:
        """Nicht realisierter Gewinn/Verlust (0.0 falls unbekannt).

        ``use_net`` wählt ``gainNet`` (nach Gebühren) statt ``gainGross``.
        """
        if self.unrealizedGains is None:
            return 0.0
        value = self.unrealizedGains.gainNet if use_net else self.unrealizedGains.gainGross
        if value is None:
            # Falls die gewünschte Variante fehlt, die andere versuchen.
            value = self.unrealizedGains.gainGross if use_net else self.unrealizedGains.gainNet
        return value if value is not None else 0.0

    @property
    def identifier(self) -> Optional[str]:
        if self.id:
            return self.id
        return self.asset.symbol if self.asset else None

    @property
    def asset_type(self) -> Optional[str]:
        return self.asset.type if self.asset else None

    @property
    def is_sold(self) -> bool:
        return bool(self.position.isSold) if self.position else False

    @property
    def name(self) -> str:
        if self.asset is not None and self.asset.name:
            return self.asset.name
        return self.identifier or "Unbekannt"


@dataclass
class PerformanceResponse:
    """Antwort des Parqet-Endpunkts ``POST /performance``.

    Interessant ist die Liste der ``holdings`` mit ihren ``unrealizedGains``.
    Die Wurzel wird tolerant behandelt: sie darf direkt eine Liste sein oder die
    Holdings unter ``holdings``/``positions`` führen.
    """

    holdings: list[PerformanceHolding] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Any) -> "PerformanceResponse":
        if isinstance(data, list):
            raw_holdings: list[Any] = data
        elif isinstance(data, dict):
            raw_holdings = data.get("holdings") or data.get("positions") or []
        else:
            raw_holdings = []
        return cls(
            holdings=[
                PerformanceHolding.from_dict(h)
                for h in raw_holdings
                if isinstance(h, dict)
            ]
        )


@dataclass
class ActivitiesResponse:
    interval: Optional[Interval] = None
    hasMore: Optional[bool] = None
    offset: Optional[int] = None
    totalCount: Optional[int] = None
    activities: list[Activity] = field(default_factory=list)
    portfolioSnapshots: list[Any] = field(default_factory=list)
    holdingSnapshots: list[Any] = field(default_factory=list)
    relatedEvents: list[RelatedEvent] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ActivitiesResponse":
        interval = data.get("interval")
        return cls(
            interval=Interval.from_dict(interval) if isinstance(interval, dict) else None,
            hasMore=data.get("hasMore"),
            offset=data.get("offset"),
            totalCount=data.get("totalCount"),
            activities=[
                Activity.from_dict(a)
                for a in data.get("activities", [])
                if isinstance(a, dict)
            ],
            portfolioSnapshots=list(data.get("portfolioSnapshots", [])),
            holdingSnapshots=list(data.get("holdingSnapshots", [])),
            relatedEvents=[
                RelatedEvent.from_dict(e)
                for e in data.get("relatedEvents", [])
                if isinstance(e, dict)
            ],
        )
