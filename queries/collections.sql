-- Aylık tahsilatlar. Tablo/kolon adlarını kendi veritabanınıza göre düzenleyin.
-- Grafik için ilk kolon kategori, ikinci kolon sayısal değer olmalıdır.
SELECT
    FORMAT(p.PaymentDate, 'yyyy-MM') AS Ay,
    SUM(p.Amount)                    AS ToplamTahsilat
FROM dbo.Payments p
WHERE p.PaymentDate >= DATEADD(MONTH, -12, GETDATE())
GROUP BY FORMAT(p.PaymentDate, 'yyyy-MM')
ORDER BY Ay;
