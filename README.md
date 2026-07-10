For the tax calculation, you need the response JSON of parqet's POST /performance and add it as input parameter when starting the python script. 

Additionally, you need the kirchensteuer value as an integer (0, 8, or 9)

example execution: 
```
python tax.py postPerformanceResponse.json 9
```
