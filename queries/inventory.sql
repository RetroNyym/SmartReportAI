-- Stok durumu. Tablo/kolon adlarını kendi veritabanınıza göre düzenleyin.
SELECT
    p.ProductCode  AS UrunKodu,
    p.ProductName  AS UrunAdi,
    i.QuantityOnHand AS StokMiktari,
    i.ReorderLevel   AS MinStok
FROM dbo.Products p
JOIN dbo.Inventory i ON i.ProductId = p.ProductId
ORDER BY i.QuantityOnHand ASC;
