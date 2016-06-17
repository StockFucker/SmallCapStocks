SmallCapStocks
==========
**A small capacity stocks strategy, calculate the market value of stocks, and buy the minimum several stocks.**                 
**SUPPORT python2**
_________________
    
1\. Including stocks start with 0, 3, 6           
2\. Excluding stocks with ST or risk notification from [sse, shanghai stock exchange](http://www.sse.com.cn/disclosure/listedinfo/riskplate/list/)                   
3\. Excluding stocks with suspended or limit up                      
       
        
Trade price decision
______________________

1\.Get ten gear price from [leverfun API](https://app.leverfun.com/timelyInfo/timelyOrderForm?stockCode=300151), and comparison the own balance and commission volumes, return the corresponding price         
2\.Premium paramter is important, avoid risk of the commission volumes equal to own banlance, the initial value of premium is 1.02.                 
       
Dependency
===============
[easytrader](https://github.com/shidenggui/easytrader)         

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
