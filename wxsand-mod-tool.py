import requests
from bs4 import BeautifulSoup
import re
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import webbrowser

class WikiScraper():
    def __init__(self, root):
        self.root = root
        self.root.title("WxSand Mod Tool")
        self.root.configure(background="grey")

        # Frames
        listframe = tk.LabelFrame(root, text="List of Mods", background="grey")
        listframe.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        optionsframe = tk.LabelFrame(root, text="Options", background="grey")
        optionsframe.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # Listbox with Scrollbar
        self.listbox = tk.Listbox(listframe, width=50, height=20)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(listframe, orient=tk.VERTICAL, command=self.listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=scrollbar.set)

        #Calls the file of links to the Wiki.
        self.load_links_from_file('wiki-links.txt')

        # Buttons
        downloadbtn = tk.Button(optionsframe, text="Download Mod", command=self.downloadbar)
        downloadbtn.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        webbtn = tk.Button(optionsframe, text="View Wiki", command=self.browse_wiki)
        webbtn.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        helpbtn = tk.Button(optionsframe, text="Help", command=self.open_help)
        helpbtn.grid(row=2, column=0, padx=5, pady=5, sticky="w")

        #Progress Bar
        self.progbar = ttk.Progressbar(optionsframe)
        self.progbar.grid(row=3, column=0, padx=5, pady=5, sticky="nsew")
        self.progbar["maximum"] = 100


        # Configure grid weights for responsiveness
        root.grid_columnconfigure(0, weight=1)
        root.grid_columnconfigure(1, weight=1)
        root.grid_rowconfigure(0, weight=1)

    #Load and change data from list of wiki links to a more readable format for the application
    def load_links_from_file(self, wikilist):
        self.listbox.delete(0, tk.END)
        with open(wikilist, 'r') as file:
            for line in file:
                link = line.strip()
                if link.startswith("*~~") and link.endswith("~~*"):
                    display_text = link
                else:
                    start_index = link.find("wiki/index.php/") + len("wiki/index.php/")
                    if start_index != -1:
                        display_text = link[start_index:]
                    else:
                        display_text = link
                self.listbox.insert(tk.END, display_text)

    #Popup help menu
    def open_help(self):
        popup = tk.Toplevel(self.root)
        popup.title("Help")
        label = tk.Label(popup, text="Please check out the repo for more assistance:\nhttps://github.com/oleskatony/wxsand-mod-tool")
        label.pack(pady=10)
        btn_close = tk.Button(popup, text="Close", command=popup.destroy)
        btn_close.pack(pady=10)

    #Launch the wiki page of the selected mod
    def browse_wiki(self):
        selected_mod = self.listbox.curselection()
        if selected_mod:
            selected_item = self.listbox.get(selected_mod)
            with open('wiki-links.txt', "r") as file:
                for line in file:
                    if selected_item in line:
                        url = line.strip()
                        break
            if "url" in locals():
                webbrowser.open(url)
            else:
                print("Selected item not found in the list.")

    #Function to play progress bar and begin download
    def downloadbar(self):
        current_value = self.progbar["value"]
        max_value = self.progbar["maximum"]
        increment = 5
        delay = 100  # Delay in milliseconds (adjust as needed)
        
        def update_progress():
            nonlocal current_value
            nonlocal increment
            
            if current_value < max_value:
                new_value = min(current_value + increment, max_value)
                self.progbar["value"] = new_value
                current_value = new_value
                self.root.after(delay, update_progress)
            else:
                # When the progress bar reaches max_value, call scrape_wiki()
                self.scrape_wiki()  # Use self to refer to the method within the class
                self.progbar["value"] = 0

        
        update_progress()


    #Scrapes the raw code from the wiki and saves the text file in the users perfered directory
    def scrape_wiki(self):
        selected_mod = self.listbox.curselection()
        if selected_mod:
            selected_item = self.listbox.get(selected_mod)
            with open('wiki-links.txt', "r") as file:
                for line in file:
                    if selected_item in line:
                        url = line.strip()
                        break
            if "url" in locals():
                response = requests.get(url)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    data_elements = soup.find_all('pre')
                    mod_title_element = soup.find('h1', class_='firstHeading')
                    mod_title = mod_title_element.text.strip()
                    mod_title = re.sub(r'[^\w.-]', '', mod_title)
                    filename = f"{mod_title}.txt"
                    directory = filedialog.askdirectory()
                    with open(f"{directory}/{filename}", 'w', encoding='utf-8') as file:
                        file.write(f"# Filename: {filename}\n\n")
                        for element in data_elements:
                            file.write(element.get_text(separator='\n') + '\n')
                    print(f"Data has been scraped and saved to '{filename}' file.")
                else:
                    print("Failed to retrieve data from the URL:", url)
            else:
                print("Selected item not found in the list.")

root = tk.Tk()
WikiScraper(root)
root.mainloop()