-- Aylık satış özeti. Tablo/kolon adlarını kendi veritabanınıza göre düzenleyin.
-- Grafik için ilk kolon kategori, ikinci kolon sayısal değer olmalıdır.
SELECT
    FORMAT(o.OrderDate, 'yyyy-MM') AS Ay,
    SUM(o.TotalAmount)             AS ToplamSatis,
    COUNT(*)                       AS SiparisSayisi
FROM dbo.Orders o
WHERE o.OrderDate >= DATEADD(MONTH, -12, GETDATE())
GROUP BY FORMAT(o.OrderDate, 'yyyy-MM')
ORDER BY Ay;
