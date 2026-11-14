from openai import OpenAI

from config.settings import settings
from reports.models import ReportResult


def generate_summary(results: list[ReportResult]) -> str:
    """Ask the LLM for a short Turkish executive summary based on the data and detected insights."""
    if not settings.openai_api_key:
        return "AI özeti devre dışı (OPENAI_API_KEY tanımlı değil)."

    sections = []
    for result in results:
        section = f"### {result.name} ({len(result.df)} satır)\n{result.df.head(30).to_csv(index=False)}"
        if result.insights:
            section += "\nTespit edilen öngörüler:\n" + "\n".join(f"- {line}" for line in result.insights)
        sections.append(section)

    prompt = (
        "Aşağıdaki iş verilerini incele ve yönetici için Türkçe bir özet yaz.\n"
        "- En önemli 3-5 bulguyu madde madde belirt.\n"
        "- Tespit edilen öngörüleri dikkate al ve nedenleri hakkında yorum yap.\n"
        "- Sayısal değerleri mümkün olduğunca kullan.\n"
        "- Veride olmayan bilgi uydurma.\n\n" + "\n\n".join(sections)
    )

    client = OpenAI(api_key=settings.openai_api_key)
    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": "Sen deneyimli bir iş analisti asistanısın."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()
