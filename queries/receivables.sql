-- Cari hesap bakiyeleri. Tablo/kolon adlarını kendi veritabanınıza göre düzenleyin.
SELECT
    c.AccountCode          AS CariKodu,
    c.AccountName          AS CariAdi,
    SUM(i.Debit - i.Credit) AS Bakiye
FROM dbo.Accounts c
JOIN dbo.AccountTransactions i ON i.AccountId = c.AccountId
GROUP BY c.AccountCode, c.AccountName
HAVING SUM(i.Debit - i.Credit) <> 0
ORDER BY Bakiye DESC;
