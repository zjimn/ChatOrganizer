import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox, ttk

from event.event_bus import event_bus


class SearchableScrolledText(tk.Frame):
    def __init__(self, root, parent, **kwargs):
        super().__init__(parent)

        # Create a ScrolledText widget
        self.count_label = None
        self.count_text = None
        self.entry = None
        self.output_text = scrolledtext.ScrolledText(self, **kwargs)
        self.output_text.pack(fill=tk.BOTH, expand=True)

        # Bind Ctrl+F to trigger search dialog
        self.output_text.bind("<Control-f>", self.trigger_search_dialog)
        self.output_text.bind("<Control-F>", self.trigger_search_dialog)

        # Initialize search state
        self.search_results = []
        self.current_index = -1
        self.query = ""  # Initialize query variable to store the search text

        # Tag configurations
        self.output_text.tag_config("highlight", background="blue", foreground="white")
        self.output_text.tag_config("current_highlight", background="yellow", foreground="black")

        # Initialize buttons for navigation
        self.prev_button = None
        self.next_button = None
        self.search_window = None

        # Bind the parent window's configure event to update the search window's position
        parent.bind_all("<Configure>", lambda event: self.update_search_window_position(parent))
        self.create_search_window(parent)
        self.close_window()

    def trigger_search_dialog(self, event=None):
        self.display_window()

    def search_text(self, query):
        self.output_text.tag_remove("highlight", "1.0", tk.END)  # Clear previous highlights
        self.search_results = []
        self.current_index = -1

        self.output_text.config(state=tk.NORMAL)  # Enable editing for tagging

        # Find matches and highlight them
        start = "1.0"
        while True:
            start = self.output_text.search(query, start, stopindex=tk.END)
            if not start:
                break
            end = f"{start}+{len(query)}c"
            self.output_text.tag_add("highlight", start, end)
            self.search_results.append(start)
            start = end

        self.output_text.config(state=tk.DISABLED)  # Re-disable editing

        if self.search_results:
            self.current_index = 0
            self.jump_to_result(self.current_index)
            self.update_navigation_buttons(True)  # Enable buttons if matches are found
        else:
            self.current_index = -1
            #messagebox.showinfo("Search", "No matches found.", parent=self)
            self.update_navigation_buttons(False)  # Disable buttons if no matches found

    def clear_highlight(self):
        self.output_text.tag_remove("highlight", "1.0", tk.END)  # Clear previous
        self.output_text.tag_remove("current_highlight", "1.0", tk.END)  # Clear previous

    def jump_to_result(self, index):
        if 0 <= index < len(self.search_results):
            pos = self.search_results[index]
            self.output_text.see(pos)  # Scroll to match
            self.output_text.tag_remove("current_highlight", "1.0", tk.END)  # Clear previous
            self.output_text.tag_add("current_highlight", pos, f"{pos}+{len(self.query)}c")

    def create_search_window(self, parent):
        # Create a Toplevel window without title bar

        search_window = tk.Toplevel(parent)
        search_window.wm_attributes("-topmost", 1)
        search_window.overrideredirect(True)  # Remove window decorations

        # Save reference to the search window
        self.search_window = search_window

        # Set initial position
        self.update_search_window_position(parent)

        # Create input field
        self.entry = tk.Entry(search_window, width=20)
        self.entry.pack(side=tk.LEFT, padx=5, pady=5)


        # Create Previous and Next buttons
        self.count_text = tk.Label(search_window)
        self.count_label = tk.Label(search_window, text="0/0")
        self.count_label.pack(side=tk.LEFT, fill=tk.BOTH, padx=5)
        # Create Previous and Next buttons
        self.prev_button = ttk.Button(search_window, text="上一条", command=lambda: self.previous_result())
        self.prev_button.pack(side=tk.LEFT, padx=5)
        self.next_button = ttk.Button(search_window, text="下一条", command=lambda: self.next_result())
        self.next_button.pack(side=tk.LEFT, padx=5)
        # Create Search button
        search_button = ttk.Button(search_window, text="关闭", command=lambda: self.close_window())
        search_button.pack(side=tk.LEFT, padx=5)

        # Bind KeyRelease to trigger search on text input
        self.entry.bind("<KeyRelease>", lambda event: self.start_search(self.entry.get()))
        event_bus.subscribe("CloseOutputWindow",self.close_window)


    def close_window(self):
        self.search_window.withdraw()
        self.clear_highlight()

    def display_window(self):
        self.search_window.deiconify()
        self.entry.delete(0, tk.END)
        self.entry.focus()

    def set_count_label(self, current_index, total):
        current_index+=1
        self.count_label.config(text=f"{current_index}/{total}")

    def start_search(self, query):
        if query:
            self.query = query
            self.search_text(query)
            total = len(self.search_results)
            self.set_count_label(self.current_index, total)
            if total == 0:
                self.clear_highlight()
        else:
            self.clear_highlight()
            self.search_results = []
            self.set_count_label(-1, 0)
            self.update_navigation_buttons(False)
            self.clear_highlight()

    def previous_result(self):
        if self.search_results:
            total = len(self.search_results)
            self.current_index = (self.current_index - 1) % total
            self.jump_to_result(self.current_index)
            self.set_count_label(self.current_index, total)

    def next_result(self):
        if self.search_results:
            total = len(self.search_results)
            self.current_index = (self.current_index + 1) % total
            self.jump_to_result(self.current_index)
            self.set_count_label(self.current_index, total)

    def update_navigation_buttons(self, enable):
        if enable:
            self.prev_button.config(state=tk.NORMAL)
            self.next_button.config(state=tk.NORMAL)
        else:
            self.prev_button.config(state=tk.DISABLED)
            self.next_button.config(state=tk.DISABLED)

    def update_search_window_position(self, parent):
        if hasattr(self, "search_window") and self.search_window.winfo_exists():
            # Get the position of the parent window
            parent_x = parent.winfo_rootx()
            parent_y = parent.winfo_rooty()
            parent_width = parent.winfo_width()

            # Set the position of the search window (relative to parent window)
            self.search_window.geometry(f"500x50+{parent_x + parent_width - 500}+{parent_y + 0}")
            self.search_window.overrideredirect(True)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Searchable ScrolledText Example")

    # Create a frame containing the searchable text widget
    text_component = SearchableScrolledText(root, wrap=tk.WORD)
    text_component.pack(fill=tk.BOTH, expand=True)

    # Add some example text
    for i in range(1, 101):
        text_component.output_text.insert(tk.END,
                                          f"This is line {i}. Example text for testing the search functionality.\n")

    text_component.output_text.config(state=tk.DISABLED)  # Disable editing

    root.mainloop()