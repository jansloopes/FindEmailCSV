
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from tkinter import Menu, Text, Toplevel, Scrollbar, filedialog
import hashlib
import re
import pandas as pd
import threading
import os
import logging

__author__ = 'Jan Hellings'
__copyright__ = 'Copyright 2024, Jan Hellings'
__credits__ = ['Chatcpt']
__license__ = 'GNU'
__version__ = '0.1'
__maintainer__ = 'Jan Hellings'
__email__ = 'Jan@famhellings.nl'
__status__ = 'Prototype'

# Configure logging
logging.basicConfig(
    filename='email_finder.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class EmailFinderApp:
    def __init__(self, root):
        """
        Initializes the EmailFinderApp instance.

        Args:
            root (tkinter.Tk): The root tkinter window.

        Initializes the following instance variables:
            - root (tkinter.Tk): The root tkinter window.
            - label (ttk.Label): The label widget displaying a message.
            - open_button (ttk.Button): The button widget to open a CSV file.
            - save_button (ttk.Button): The button widget to save the results.
            - hash_button (ttk.Button): The button widget to generate a hash.
            - result_text (tk.Text): The text widget to display the results.
            - progress (ttk.Progressbar): The progress bar widget.
            - status_label (ttk.Label): The label widget to display the status.
            - emails (list): The list to store the email addresses.
        """
        self.root = root
        self.root.title("Email Finder in CSV files V0.1")
        self.root.geometry("750x550")
        
        self.label = ttk.Label(root, text="Select a CSV file to find email addresses:")
        self.label.grid(row=0, column=0, padx=10, pady=10, columnspan=4)
        
        self.open_button = ttk.Button(root, text="Open CSV File and find email addresses", command=self.open_file)
        self.open_button.grid(row=1, column=0, padx=10, pady=5)
        
        self.save_button = ttk.Button(root, text="Save Results", command=self.save_results)
        self.save_button.grid(row=1, column=1, padx=10, pady=5)
        
        self.hash_button = ttk.Button(root, text="Generate Hash", command=self.generate_hash)
        self.hash_button.grid(row=1, column=2, padx=10, pady=5)
        
        self.help_button = ttk.Button(root, text="Help", command=self.show_help)
        self.help_button.grid(row=1, column=3, padx=10, pady=5)
        
        self.result_text = tk.Text(root, height=20, width=80, state=tk.DISABLED)
        self.result_text.grid(row=2, column=0, padx=10, pady=10, columnspan=3)
        
        self.progress = ttk.Progressbar(root, orient=tk.HORIZONTAL, length=600, mode='determinate')
        self.progress.grid(row=3, column=0, padx=10, pady=10, columnspan=3)
        
        self.status_label = ttk.Label(root, text="Status: Ready")
        self.status_label.grid(row=4, column=0, padx=10, pady=5, columnspan=3)
        
        self.emails = []

    def open_file(self)-> None:
        """
        Opens a file dialog and processes the selected file.
        
        Open a file dialog to select a CSV file. If a file is selected, check if a corresponding hash file exists.
        If the hash file exists, verify its integrity. If the hash file is not valid, show an error message.
        Start a new thread to process the selected file. Update the progress bar and status label.
        Log the processing start.

        Parameters:
            self (object): The instance of the class.

        Returns:
            None

        """
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            hash_file_path = file_path + '.sha256'
            if os.path.exists(hash_file_path):
                if not self.verify_hash(file_path, hash_file_path):
                    messagebox.showerror("Hash Mismatch", "The file hash does not match the saved hash. The file may have been tampered with.")
                    logging.warning(f"Hash mismatch for file: {file_path}")
                    return
            self.progress.start()
            self.status_label.config(text="Status: Processing file...")
            threading.Thread(target=self.find_emails, args=(file_path,)).start()
            logging.info(f"Processing started for file: {file_path}")

    def generate_hash(self):
        """
        Generates a SHA256 hash for a selected CSV file and saves it to a separate file.
        This function prompts the user to select a CSV file using a file dialog. It then reads the contents of the file, calculates the SHA256 hash using the hashlib module, and saves the hash to a separate file with the same name as the original file but with a '.sha256' extension. The hash file includes a header line with the text 'Hash sha256 for file: ' followed by the path of the original file.

        Parameters:
            self (EmailFinderApp): The instance of the EmailFinderApp class.

        Returns:
            None
        """ 
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            hash_file_path = file_path + '.sha256'
            with open(file_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            with open(hash_file_path, 'w') as hash_file:
                hash_file.write('Hash sha256 for file: ' + file_path + '\n')
                hash_file.write(file_hash)
            messagebox.showinfo("Hash Generated", f"Hash file saved as {hash_file_path}")
            logging.info(f"Hash generated for file: {file_path} and saved as {hash_file_path}")

    def verify_hash(self, file_path: str, hash_file_path: str) -> bool:
        """
        Verify the integrity of a file by comparing its SHA256 hash with a saved hash.

        Args:
            file_path (str): The path to the file to be verified.
            hash_file_path (str): The path to the file containing the saved hash.

        Returns:
            bool: True if the hashes match, False otherwise.

        This function calculates the SHA256 hash of the file specified by `file_path` and compares it with the hash stored in the file specified by `hash_file_path`. If the hashes match, the function logs a success message and returns True. If the hashes do not match, the function logs a warning message and returns False.

        Raises:
            FileNotFoundError: If either `file_path` or `hash_file_path` does not exist.
            PermissionError: If the user does not have permission to read either `file_path` or `hash_file_path`.
        """
        with open(file_path, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        with open(hash_file_path, 'r') as hash_file:
            saved_hash = hash_file.read().strip()
        if file_hash == saved_hash:
            logging.info(f"Hash verification successful for file: {file_path}")
            return True
        else:
            logging.warning(f"Hash verification failed for file: {file_path}")
            return False

    def find_emails(self, file_path:str):
        """
        Reads a CSV file from the given `file_path` and extracts all email addresses found in the file.

        Args:
            file_path (str): The path to the CSV file.

        Returns:
            None

        This function reads a CSV file from the given `file_path` and extracts all email addresses found in the file.
        It uses the `pd.read_csv()` function from the pandas library to read the CSV file in chunks.
        The `chunksize` parameter is set to 1000 to process the file in smaller chunks for better performance.
        The `on_bad_lines` parameter is set to 'warning' to log a warning message for any bad lines encountered.

        The function then defines a regular expression pattern to match email addresses.
        It iterates over each chunk of the CSV file and converts it to a string using the `to_string()` function.
        It then uses the `re.findall()` function to find all email addresses in the
        """
        try:
            df = pd.read_csv(file_path, dtype=str, chunksize=1000,on_bad_lines='warn')
            logging.warn(f"File read: {file_path}")
            email_pattern = re.compile('[a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]{2,}')
            self.emails = []
            
            for chunk in df:
                text_data = chunk.to_string(index=False)
                self.emails.extend(re.findall(email_pattern, text_data))
            
            self.emails = list(set(self.emails))  # Remove duplicates
            
            self.result_text.config(state=tk.NORMAL)
            self.result_text.delete('1.0', tk.END)
            self.result_text.insert(tk.END, "\n".join(self.emails))
            self.result_text.config(state=tk.DISABLED)
            
            self.status_label.config(text=f"Status: Found {len(self.emails)} email addresses.")
            messagebox.showinfo("Results", f"Found {len(self.emails)} email addresses.")
            logging.info(f"Found {len(self.emails)} email addresses in file: {file_path}")
        except Exception as e:
            self.status_label.config(text="Status: Error occurred")
            messagebox.showerror("Error", f"An error occurred: {e}")
            logging.error(f"Error processing file: {file_path}, Error: {e}")
        finally:
            self.progress.stop()
            
    def save_results(self)-> None:
        """
        Save the results to a file.

        This function prompts the user to select a file path to save the results. If there are no emails to save,
        a messagebox is displayed with the message "No emails to save." and the function returns.

        If the user selects a file path, the function attempts to open the file in write mode and write the
        emails to the file. If successful, a messagebox is displayed with the message "Results saved to {file_path}"
        and the function logs the successful save. If an error occurs while saving the file, a messagebox is
        displayed with the message "Could not save the file: {e}" and the function logs the error.

        Parameters:
            self (EmailFinderApp): The instance of the EmailFinderApp class.

        Returns:
            None
        """
        if not self.emails:
            messagebox.showinfo("No Results", "No emails to save.")
            logging.info("No emails to save.")
            return
        
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write("\n".join(self.emails))
                messagebox.showinfo("Saved", f"Results saved to {file_path}")
                logging.info(f"Results saved to file: {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save the file: {e}")
                logging.error(f"Error saving file: {file_path}, Error: {e}")
    def show_help(self):
        """
        Displays the help content in a separate window.

        This function creates a new Toplevel window titled "Help" and displays the help content in a Text widget.
        The help content is read from a file named 'help.txt'. If the file is not found, an error message is displayed
        in the Text widget and a warning message is logged.

        Parameters:
            self (EmailFinderApp): The instance of the EmailFinderApp class.

        Returns:
            None
        """
    
        help_window = Toplevel(self.root)
        help_window.title("Help")
    
        text_area = Text(help_window, wrap='word')
        scroll_bar = Scrollbar(help_window, orient='vertical', command=text_area.yview)
        text_area.configure(yscrollcommand=scroll_bar.set)

        scroll_bar.pack(side='right', fill='y')
        text_area.pack(side='left', fill='both', expand=True)

    # Read the help file
        try:
            with open('help.txt', 'r') as file:
                help_content = file.read()
                text_area.insert('1.0', help_content)
        except FileNotFoundError:
            text_area.insert('1.0', "Help file 'help.txt' not found. Please check the path and try again.") 
            logging.error("Help file 'help.txt' not found. Please check the path and try again.")

        


def main():
    """
    Runs the main function of the application.

    This function initializes a root tkinter window and creates an instance of the EmailFinderApp class.
    It then starts the main event loop of the application by calling the `mainloop()` method on the root window.

    Parameters:
    None

    Returns:
    None
    """
    root = tk.Tk()
    app = EmailFinderApp(root)
    root.mainloop()

    
if __name__ == "__main__":
    main()
    