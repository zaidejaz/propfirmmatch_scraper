import requests
from bs4 import BeautifulSoup
import csv
import time

def extract_cell_data(cell):
    # Extract text from various possible elements
    text_elements = cell.find_all(text=True, recursive=False)
    img_elements = cell.find_all('img', alt="Checkmark icon")
    
    if img_elements:
        return "Yes"  # If there's a checkmark image, interpret as "Yes"
    elif text_elements:
        return ' '.join(text.strip() for text in text_elements if text.strip())
    else:
        # Check for nested elements
        nested_text = cell.find(text=True, recursive=True)
        return nested_text.strip() if nested_text else ""

def scrape_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    data = []
    info_wrappers = soup.find_all('div', class_='more-info-wrapper')
    
    for wrapper in info_wrappers:
        row_data = {}
        cells = wrapper.find_all('div', class_=['ch-cell-item', 'ch-cell-item last'])
        
        for i in range(0, len(cells), 2):
            if i + 1 < len(cells):
                key = extract_cell_data(cells[i])
                value = extract_cell_data(cells[i + 1])
                row_data[key] = value
        
        data.append(row_data)
    
    return data

def main():
    base_url = 'https://www.propfirmmatch.com/'
    current_url = base_url
    all_data = []
    
    while True:
        print(f"Scraping: {current_url}")
        page_data = scrape_page(current_url)
        all_data.extend(page_data)
        
        response = requests.get(current_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        next_button = soup.find('a', id='Pagination', class_='w-pagination-next')
        
        if not next_button or 'style' in next_button.attrs and 'display:none' in next_button['style']:
            break
        
        current_url = base_url + next_button['href']
        time.sleep(1)  # Be polite, wait a second between requests
    
    # Save data to CSV
    if all_data:
        # Get all unique keys across all dictionaries
        keys = set()
        for item in all_data:
            keys.update(item.keys())
        
        with open('propfirmmatch_data.csv', 'w', newline='', encoding='utf-8') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=list(keys))
            dict_writer.writeheader()
            dict_writer.writerows(all_data)
        print("Data saved to propfirmmatch_data.csv")
    else:
        print("No data was scraped.")

if __name__ == "__main__":
    main()