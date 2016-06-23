SmallCapStocks
==========
**xueqiu branch**
**A small capacity stocks strategy, calculate the market value of stocks, and buy the minimum several stocks.**                 
**SUPPORT python2**
_________________
    
1\. Including stocks start with 0, 3, 6           
2\. Excluding stocks with ST or risk notification from [sse, shanghai stock exchange](http://www.sse.com.cn/disclosure/listedinfo/riskplate/list/)                   
3\. Excluding stocks with suspended or limit up                      
       
      
Dependency
===============
[easytrader](https://github.com/shidenggui/easytrader)         

I have changed some source codes from easytrader, and it's easy to adjust position.          
You can get the source code [from my fork easytrader](https://github.com/xdbaqiao/easytrader)                 
Install easytrader, you need install logbook, demjson, use following command:         
       
       sudo pip install logbook         
       sudo pip install demjson
      
<del>[numpy]</del>      
<del>[pandas]</del>         
<del>[tushare]</del>
<del>[easyquotation]</del>       
                
        
LICENSE       
============
    Copyright 2016 StockFucker            
    
    All codes is licensed under GPLv2.             
    This means you can use those codes according to the license on a case-by-case basis.         
    However, you cannot modify it and distribute it without supplying the source.                
