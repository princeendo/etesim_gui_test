# -*- coding: utf-8 -*-

# Tkinter imports
import tkinter as tk

class guiTextLabel():
    def __init__(self, parent, style, **kwargs):
        self.text = tk.StringVar(parent, '')
        self.kwargs = kwargs
        self.label = tk.Label(parent, **kwargs, textvariable=self.text)
        
        if 'text' in self.kwargs:
            self.text.set(self.kwargs['text'])
        
        self.show = self._pack if style == 'pack' else self._grid
        self.hide = self._pack_forget if style == 'pack' else self._grid_forget
        
    def _pack(self):
        self.label.pack(**self.kwargs)
        
    def _pack_forget(self):
        self.label.pack_forget()    
    
    def _grid(self):
        self.label.grid(**self.kwargs)
        
    def _grid_forgt(self):
        self.label.grid_forget()
    
    def set(self, newText):
        self.text.set(newText)
    
    def get(self,):
        self.text.get()