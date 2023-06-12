
import tkinter.ttk as ttk
import tkinter as tk

import cogni_scan.front_end.cfc.view as view


class LeftView(ttk.Treeview, view.View):
    
    def eventHandler(self, item_selected):
        print("here", item_selected)
        cur_item = self.focus()
        values = self.item(cur_item)
        mri = values["values"][0]
        self.getDocument().setActiveMri(mri, self)

    def update(self):
        """Called to update the view.

        (Abstract method from base class)

        Needs to be implemented by the client code.
        """
        self.heading('#0', text='Subject ID', anchor=tk.W)
        self.delete(*self.get_children())
        for mri in self.getDocument().getMRIs():
            y = self.insert(
                '',
                tk.END,
                text=mri.getCaption(),
                iid=mri.getFilePath(),
                open=False,
                values=[mri.getFilePath()]
            )
            aaa = 1111
        self.bind('<<TreeviewSelect>>', self.eventHandler)


if __name__ == '__main__':
    v = LeftView()
