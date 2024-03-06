import requests
from bs4 import BeautifulSoup
import os
import re
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import webbrowser

##########GUI

class wikiscraper():
    def __init__(self, root):
        self.root = root
        self.root.title("WxSand Mods")
        self.root.geometry("800x600+500+200")
        
        # Frames
        listframe = tk.LabelFrame(root, text="List of Mods", width=500, height=500, background="grey")
        listframe.pack(side=tk.LEFT, padx=0, pady=0, fill=tk.BOTH, expand=True)
        
        optionsframe = tk.LabelFrame(root, text="Options", width=190, height=1600, background="grey")
        optionsframe.pack(side=tk.TOP, padx=0, pady=0, fill=tk.BOTH)
        
        # Listbox with Scrollbar
        self.listbox = tk.Listbox(listframe, width=50, height=20)
        self.listbox.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(listframe, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.listbox.yview)
        
        self.load_links_from_file('wiki-links.txt')

        #Buttons
        downloadbtn = tk.Button(optionsframe,text="Download Mod", command=self.scrapewiki)
        downloadbtn.place(x=10, y=10)
        webbtn = tk.Button(optionsframe,text="View Wiki", command=self.browsewiki)
        webbtn.place(x=120, y=10)
        helpbtn = tk.Button(optionsframe,text="Help", command=self.open_help)
        helpbtn.place(x=10, y=40)


    def load_links_from_file(self, wikilist):
        # Clear the existing items in the listbox
        self.listbox.delete(0, tk.END)
        # Open the text file containing website links
        with open(wikilist, 'r') as file:
            # Read each line from the file
            for line in file:
                # Remove leading and trailing whitespace
                link = line.strip()
                linkpure = line.strip()
                # Check if the line contains exceptions
                if link.startswith("*~~") and link.endswith("~~*"):
                    display_text = link
                else:
                    # Extract the part of the link that comes after "wiki/index.php/"
                    start_index = link.find("wiki/index.php/") + len("wiki/index.php/")
                    if start_index != -1:
                        display_text = link[start_index:]
                    else:
                        display_text = link
                # Insert the modified link into the listbox
                self.listbox.insert(tk.END, display_text)

    def open_help(self):
        popup = tk.Toplevel(self.root)
        popup.title("Popup Window")
        popup.geometry("200x100")
        
        label = tk.Label(popup, text="This is a popup window")
        label.pack(pady=10)
        
        btn_close = tk.Button(popup, text="Close", command=popup.destroy)
        btn_close.pack(pady=10)
##########GUI
    def browsewiki(self):
        # URL of the wiki page you want to scrape
        selected_mod = self.listbox.curselection()
        if selected_mod:
            selected_item = self.listbox.get(selected_mod)
            # Read original list to compare
            with open('wiki-links.txt', "r") as file:
                for line in file:
                    if selected_item in line:
                        url = line.strip()
                        break
            if "url" in locals():
                # Open the URL in the default web browser
                webbrowser.open(url)
            else:
                print("Selected item not found in the list.")

    def scrapewiki(self):
        # URL of the wiki page you want to scrape
        selected_mod = self.listbox.curselection()
        if selected_mod:
            selected_item = self.listbox.get(selected_mod)
            #Read original list to compare
            with open('wiki-links.txt', "r") as file:
                for line in file:
                    if selected_item in line:
                        url = line.strip()
                        break
            if "url" in locals():
                # Send GET request to URL
                response = requests.get(url)
                # Check if the request was successful (status code 200)
                if response.status_code == 200:
                    # Parse the HTML content of the page
                    soup = BeautifulSoup(response.text, 'html.parser')
                    # Scrape code from wiki
                    data_elements = soup.find_all('pre') #code
                    mod_title_element = soup.find('h1', class_='firstHeading')
                    # Process the mod title
                    mod_title = mod_title_element.text.strip()
                    mod_title = re.sub(r'[^\w.-]', '', mod_title)
                    filename = f"{mod_title}.txt"
                    # Open a text file with the mod title as the filename
                    with open(filename, 'w', encoding='utf-8') as file:
                        # Iterate over the data elements and write them to the file
                        file.write(f"# Filename: {filename}\n\n")
                        for element in data_elements:
                            file.write(element.get_text(separator='\n') + '\n')
                    print(f"Data has been scraped and saved to '{filename}' file.")
                else:
                    print("Failed to retrieve data from the URL:", url)
            else:
                print("Selected item not found in the list.")

# Creating TK Container
root = tk.Tk()
# Passing Root to MusicPlayer Class
wikiscraper(root)
# Root Window Looping
root.mainloop()