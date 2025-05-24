import requests
import csv


# Login and then copy the main page from the network tab as curl, and then use a curl convertor for cookies and headers
cookies = {}

headers = {}


accumulated_words = []

def get_details(page_number):
    api = f"https://www.seedlang.com/api/words?sort=frequency_ranking&filters[root]=true&filters[video_clip_id]=true&filters[language_id]=DE&limit=20&page={page_number}&vocab_list=true"

    response = requests.get(api, cookies=cookies, headers=headers).json()
    for i in range(0, 19+1):
        seen = set()
        word = ""
        plural = []
        translation = []

        data = response["data"][i]
        word = f"{data["singular_article"]} {data["target_text"]}" if data["word_type"]["name"] == "Noun" else data["target_text"]
        if len(data["plural_nouns"]) > 0:
            for subitem in data["plural_nouns"]:
                key = (subitem["plural_article"], subitem["target_text"])
                if key not in seen:
                    seen.add(key)
                    plural.append(f"{key[0]} {key[1]}")
        for subitem in data["translation_sources"]:
            if subitem["accepted"] == True:
                translation.append(subitem["source"]["text"])
        
        write_details(word, plural, translation, page_number)

def write_details(word, plural, translation, page_number):
    global accumulated_words

    accumulated_words.append([word, plural, translation])

    if len(accumulated_words) >= 100:
        day_number = ((page_number - 1) * 20) // 100 + 1
        filename = f"Tag_{day_number:02d}.csv"
        print(f"Processing {filename}")

        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Front", "Back"])

            for entry in accumulated_words:
                word = entry[0]
                plural_list = entry[1]
                translation_list = entry[2]

                plural = ", ".join(plural_list) if plural_list else ""
                meaning = ", ".join(translation_list)

                if plural:
                    front = f"{word} ({plural})"
                else:
                    front = word

                back = meaning

                writer.writerow([front, back])
                writer.writerow([back, front])

        accumulated_words.clear()
    
# page 842 is broken
for page in range(1, 841+1):
    try:
        get_details(page)
    except Exception as E:
        print(f"Error: {E}")