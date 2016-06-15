SmallCapStocks
==========
**A small capacity stocks strategy, calculate the market value of stocks, and buy the minimum several stocks.**                 
_________________
    
**getVolume.py:**                     
Return all stock volume infomation from sina or eastmoney, mutil-threads.    
           
**getPrices.py:**                     
Return all stock prices infomation throngh tushare API, mutil-threads.
        
Speed up your clone, use following command:       
     git clone --depth=1 https://github.com/xdbaqiao/SmallCapStocks.git        
      
Dependency
===============
numpy     
pandas        
[tushare](https://github.com/waditu/tushare)           
[easytrader](https://github.com/shidenggui/easytrader)         
[easyquotation](https://github.com/shidenggui/easyquotation)         
           
It is a so restless thing to install those dependencies.        
TODO: rewrite those code and reduce dependence.         


LICENSE       
============
    Copyright 2016 StockFucker            
    
    All codes is licensed under GPLv2.             
    This means you can use those codes according to the license on a case-by-case basis.         
    However, you cannot modify it and distribute it without supplying the source.                
