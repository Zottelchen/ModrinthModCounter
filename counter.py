import os

import pandas as pd
import requests
import requests_cache
import seaborn as sns

LOADERS = ["fabric", "rift", "ornithe", "neoforge", "modloader", "forge", "quilt", "babric", "bta-babric", "java-agent", "legacy-fabric", "liteloader", "nilloader"]
VERSIONS = [
    "1.21.10",
    "1.21.9",
    "1.21.8",
    "1.21.7",
    "1.21.6",
    "1.21.5",
    "1.21.4",
    "1.21.3",
    "1.21.2",
    "1.21.1",
    "1.21",
    "1.20.6",
    "1.20.5",
    "1.20.4",
    "1.20.3",
    "1.20.2",
    "1.20.1",
    "1.20",
    "1.19.4",
    "1.19.3",
    "1.19.2",
    "1.19.1",
    "1.19",
    "1.18.2",
    "1.18.1",
    "1.18",
    "1.17.1",
    "1.17",
    "1.16.5",
    "1.16.4",
    "1.16.3",
    "1.16.2",
    "1.16.1",
    "1.16",
    "1.15.2",
    "1.15.1",
    "1.15",
    "1.14.4",
    "1.14.3",
    "1.14.2",
    "1.14.1",
    "1.14",
    "1.13.2",
    "1.13.1",
    "1.13",
    "1.12.2",
    "1.12.1",
    "1.12",
    "1.11.2",
    "1.11.1",
    "1.11",
    "1.10.2",
    "1.10.1",
    "1.10",
    "1.9.4",
    "1.9.3",
    "1.9.2",
    "1.9.1",
    "1.9",
    "1.8.9",
    "1.8.8",
    "1.8.7",
    "1.8.6",
    "1.8.5",
    "1.8.4",
    "1.8.3",
    "1.8.2",
    "1.8.1",
    "1.8",
    "1.7.10",
    "1.7.9",
    "1.7.8",
    "1.7.7",
    "1.7.6",
    "1.7.5",
    "1.7.4",
    "1.7.3",
    "1.7.2",
    "1.6.4",
    "1.6.2",
    "1.6.1",
    "1.5.2",
    "1.5.1",
    "1.4.7",
    "1.4.6",
    "1.4.5",
    "1.4.4",
    "1.4.2",
    "1.3.2",
    "1.3.1",
    "1.2.5",
    "1.2.4",
    "1.2.3",
    "1.2.2",
    "1.2.1",
    "1.1",
    "1.0",
]

requests_cache.install_cache("api_cache", expire_after=3600)
cm = sns.light_palette("green", as_cmap=True)


def fetch_modrinth_mods(version="1.21.10", category="fabric", limit=1) -> int:
    url = "https://api.modrinth.com/v2/search"
    facets = f'[["project_type:mod"],["versions:{version}"],["categories:{category}"]]'
    params = {"limit": limit, "index": "relevance", "facets": facets}
    print(f"Fetching mods for version {version} and category {category}...")

    response = requests.get(url, params=params)
    response.raise_for_status()  # Raise an error for bad responses
    data = response.json()

    return data.get("total_hits", 0)


if __name__ == "__main__":
    columns = ["Version"]
    columns = columns.extend(LOADERS)
    df = pd.DataFrame(columns=columns)

    for version in VERSIONS:
        for loader in LOADERS:
            total_mods = fetch_modrinth_mods(version=version, category=loader)
            df.at[version, loader] = total_mods

    df.loc["Modloader Total"] = df.sum(numeric_only=True)
    df.loc[:, "Version Total"] = df.sum(numeric_only=True, axis=1)

    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_rows", None)
    pd.set_option("display.width", None)
    pd.set_option("display.colheader_justify", "center")
    pd.set_option("display.precision", 0)
    print(df)

    styled = df.style.format("{:.0f}")
    styled = styled.highlight_max(axis=1, props="color:white; font-weight:bold; background-color:#2F4C39;", subset=LOADERS)
    # styled = styled.highlight_min(axis=1, props="color:white; font-weight:bold; background-color:#C25964;", subset=LOADERS)
    styled = styled.text_gradient(cmap=cm, axis=1, subset=LOADERS)

    os.makedirs("output", exist_ok=True)
    with open("template.html", "r") as template_file:
        template_content = template_file.read()
    with open("output/index.html", "w") as output_file:
        output_content = template_content.replace("<!--REPLACE_CONTENT-->", styled.to_html())
        from datetime import datetime

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z")
        output_content = output_content.replace("<!--REPLACE_TIME-->", current_time)
        output_file.write(output_content)
