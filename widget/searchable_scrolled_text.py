import tkinter as tk
from tkinter import scrolledtext, ttk

from event.event_bus import event_bus
from widget.undo_redo_entry import UndoRedoEntry


class SearchableScrolledText(ttk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent)

        # Create a ScrolledText widget
        self.tag_backup = None
        self.style = None
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
        self.output_text.tag_config("highlight", background="blue", foreground="white", font=("微软雅黑", 15, "bold"))
        self.output_text.tag_config("current_highlight", background="yellow", foreground="black", font=("微软雅黑", 16, "bold"))

        # Initialize buttons for navigation
        self.prev_button = None
        self.next_button = None
        self.search_frame = None

        # Bind the parent window's configure event to update the search window's position
        #parent.bind_all("<Configure>", lambda event: self.update_search_window_position(parent))
        self.create_search_window(parent)
        root = parent.winfo_toplevel()
        root.bind('<Button-1>', lambda event, frame = self.search_frame: self.hide_frame(frame, event))
        self.update_navigation_buttons(False)
        self.close_window()

        self.output_text.bind("<Button-3>", self.show_context_menu)
        self.context_menu = tk.Menu(self, tearoff=0, bd=0, relief='flat')
        self.context_menu.add_command(label="复制", command=self.copy, state=tk.DISABLED)
        # self.context_menu.add_command(label="关闭", command=self.on_close_output_window)
        self.context_menu.config(borderwidth=0, relief="flat")

    def show_context_menu(self, event):
        if self.output_text.tag_ranges("sel"):
            self.context_menu.entryconfig("复制", state=tk.NORMAL)
            self.context_menu.post(event.x_root, event.y_root)

    def copy(self):
        try:
            self.output_text.clipboard_clear()
            selected_text = self.output_text.get("sel.first", "sel.last")
            self.output_text.clipboard_append(selected_text)
        except tk.TclError:
            pass

    def trigger_search_dialog(self, event=None):
        self.search_frame.place(relx=1, rely=0, anchor='ne')
        self.entry.delete(0, tk.END)
        self.entry.focus()
        self.set_count_label(0,0)
        self.update_navigation_buttons(False)
        self.backup_tags(self.output_text)

    def hide_frame(self, frame, event):
        x, y = event.x_root, event.y_root
        frame_x = frame.winfo_rootx()
        frame_y = frame.winfo_rooty()
        frame_width = frame.winfo_width()
        frame_height = frame.winfo_height()

        if frame.winfo_ismapped() and not (frame_x <= x <= frame_x + frame_width and frame_y <= y <= frame_y + frame_height):
            frame.place_forget()
            self.restore_tags(self.output_text)


    def search_text(self, query):
        query = query.lower()
        self.clear_highlight()
        self.restore_tags(self.output_text)
        self.search_results = []
        self.current_index = -1

        self.output_text.config(state=tk.NORMAL)  # Enable editing for tagging

        # Find matches and highlight them
        start = "1.0"
        while True:
            start = self.output_text.search(query, start, stopindex=tk.END, nocase=True)
            if not start:
                break
            end = f"{start}+{len(query)}c"
            self.clear_highlight_by_range( start, end)
            self.output_text.tag_add("highlight", start, end)
            self.search_results.append(start)
            start = end

        self.output_text.config(state=tk.DISABLED)  # Re-disable editing

        if self.search_results:
            self.current_index = 0
            self.jump_to_result(self.current_index)
            self.update_navigation_buttons(len(self.search_results) > 1)  # Enable buttons if matches are found
        else:
            self.current_index = -1
            self.update_navigation_buttons(False)  # Disable buttons if no matches found

    def clear_highlight(self):
        for tag in self.output_text.tag_names():
            self.output_text.tag_remove(tag, "1.0", tk.END)

    def clear_highlight_by_range(self, start, end):
        for tag in self.output_text.tag_names():
            self.output_text.tag_remove(tag, start, end)

    def backup_tags(self, text_widget):
        self.tag_backup = []
        for tag in text_widget.tag_names():
                ranges = text_widget.tag_ranges(tag)
                for i in range(0, len(ranges), 2):
                    self.tag_backup.append((tag, ranges[i], ranges[i + 1]))

    def restore_tags(self, text_widget):
        self.clear_highlight()
        for tag, start, end in self.tag_backup:
            text_widget.tag_add(tag, start, end)

    def jump_to_result(self, index):
        for i in range(len(self.search_results)):
            pos = self.search_results[i]
            self.output_text.see(pos)  # Scroll to match
            self.clear_highlight_by_range(pos, f"{pos}+{len(self.query)}c")
            self.output_text.tag_add("highlight", pos, f"{pos}+{len(self.query)}c")
        if 0 <= index < len(self.search_results):
            pos = self.search_results[index]
            self.output_text.see(pos)  # Scroll to match
            self.clear_highlight_by_range(pos, f"{pos}+{len(self.query)}c")
            self.output_text.tag_add("current_highlight", pos, f"{pos}+{len(self.query)}c")

    def create_search_window(self, parent):
        search_frame = ttk.Frame(parent, borderwidth=0, relief=tk.RAISED)
        self.search_frame = search_frame
        self.entry = UndoRedoEntry(search_frame, width=20, style="Custom.TEntry")
        self.entry.pack(side=tk.LEFT, padx=5, pady=5)
        # Create Previous and Next buttons
        self.count_text = tk.Label(search_frame)
        self.count_label = tk.Label(search_frame, text="0/0")
        self.count_label.pack(side=tk.LEFT, fill=tk.BOTH, padx=5)
        # Create Previous and Next buttons
        self.prev_button = ttk.Button(search_frame, text="上一条", command=lambda: self.previous_result())
        self.prev_button.pack(side=tk.LEFT, padx=5)
        self.next_button = ttk.Button(search_frame, text="下一条", command=lambda: self.next_result())
        self.next_button.pack(side=tk.LEFT, padx=5)
        self.search_frame.place_forget()
        # Bind KeyRelease to trigger search on text input
        self.entry.bind("<KeyRelease>", lambda event: self.start_search(self.entry.get()))
        event_bus.subscribe("CloseOutputWindow",self.close_window)



    def close_window(self):
        self.search_frame.place_forget()
        self.clear_highlight()
        self.update_navigation_buttons(False)

    def set_count_label(self, current_index, total):
        current_index = total if current_index >= total else current_index + 1
        self.count_label.config(text=f"{current_index}/{total}")

    def start_search(self, query):
        if query:
            self.query = query
            self.search_text(query)
            total = len(self.search_results)
            self.set_count_label(self.current_index, total)
            if total == 0:
                self.restore_tags(self.output_text)
        else:
            self.restore_tags(self.output_text)
            self.search_results = []
            self.set_count_label(0, 0)
            self.update_navigation_buttons(False)
            self.restore_tags(self.output_text)

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

    # def update_search_window_position(self, parent):
    #     if hasattr(self, "search_frame") and self.search_frame.winfo_exists():
    #         # Get the position of the parent window
    #         parent_x = parent.winfo_rootx()
    #         parent_y = parent.winfo_rooty()
    #         parent_width = parent.winfo_width()
    #
    #         # Set the position of the search window (relative to parent window)
    #         self.search_frame.geometry(f"400x50+{parent_x + parent_width - 420}+{parent_y + 0}")
    #         self.search_frame.overrideredirect(True)


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