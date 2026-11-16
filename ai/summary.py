from openai import OpenAI

from config.i18n import LANGUAGE, LANGUAGES, t
from config.settings import settings
from reports.models import ReportResult


def generate_summary(results: list[ReportResult]) -> str:
    """Ask the LLM for a short executive summary in the configured language, based on the data and detected insights."""
    if not settings.openai_api_key:
        return t("ai_disabled")

    sections = []
    for result in results:
        section = f"### {result.name} ({len(result.df)} rows)\n{result.df.head(30).to_csv(index=False)}"
        if result.insights:
            section += "\nDetected insights:\n" + "\n".join(f"- {line}" for line in result.insights)
        sections.append(section)

    prompt = (
        "Review the business data below and write an executive summary for management "
        f"in {LANGUAGES[LANGUAGE]['name']}.\n"
        "- List the 3-5 most important findings as bullet points.\n"
        "- Take the detected insights into account and comment on their likely causes.\n"
        "- Use numeric values whenever possible.\n"
        "- Do not invent information that is not in the data.\n\n" + "\n\n".join(sections)
    )

    client = OpenAI(api_key=settings.openai_api_key)
    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": "You are an experienced business analyst assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()
