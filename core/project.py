import copy
from typing import Optional, List, Tuple
from core.ass_parser import AssDoc, AssStyle

class KaraokeProject:
    def __init__(self):
        self.doc: Optional[AssDoc] = None
        self.current_path: Optional[str] = None
        
        self.undo_stack: List[Tuple[List[AssStyle], Optional[str]]] = []
        self.redo_stack: List[Tuple[List[AssStyle], Optional[str]]] = []
        
    def load(self, path: str):
        self.doc = AssDoc.load(path)
        self.current_path = path
        self.undo_stack.clear()
        self.redo_stack.clear()
        self._push_state()
        
    def _push_state(self):
        if not self.doc:
            return
        state = (copy.deepcopy(self.doc.styles), self.doc.bg_color)
        self.undo_stack.append(state)
        self.redo_stack.clear()
        
    def commit_change(self):
        self._push_state()
        
    def undo(self) -> bool:
        if len(self.undo_stack) > 1:
            self.redo_stack.append(self.undo_stack.pop())
            state = self.undo_stack[-1]
            if self.doc:
                self.doc.styles = copy.deepcopy(state[0])
                self.doc.bg_color = state[1]
            return True
        return False
            
    def redo(self) -> bool:
        if self.redo_stack:
            state = self.redo_stack.pop()
            self.undo_stack.append(state)
            if self.doc:
                self.doc.styles = copy.deepcopy(state[0])
                self.doc.bg_color = state[1]
            return True
        return False

    def save(self, out_path: str):
        if self.doc:
            self.doc.save_as(out_path, bg_color_hex=self.doc.bg_color)
