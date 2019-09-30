import threading
import time

from abalone import FieldTemplate
from graphics.GraphicModule import GraphicModule


class TextGraphic(GraphicModule):

    def __init__(self, update_feq: int = 1,
                 disable_auto_draw: bool = False,
                 use_info_text: bool = True):
        super().__init__(update_feq, disable_auto_draw)

        self._info_text = ">> Turns: {0}, Dropped black: {1}, Dropped white: {2}\n" if use_info_text else None
        self._draw = self._initialized_draw

    def _build_task(self) -> threading.Thread:
        task = threading.Thread(target=self.__main_loop, args=[])
        task.daemon = True
        return task

    def __main_loop(self) -> None:
        prv_time = time.time()
        while self.sync_module.run:
            if self.feq_draw and time.time() - prv_time > 1 / self.update_feq:
                prv_time = time.time()
                self._draw()
            elif self.sync_module.sig_force_draw:
                self.sync_module.sig_force_draw = False
                self._draw()

    def _draw(self) -> None:
        pass

    def _initialized_draw(self) -> None:
        print(FieldTemplate.get_text_board(self.sync_module.base_vector), "\n", self._info_text.format(
            self.sync_module.base_vector[1], self.sync_module.base_vector[3], self.sync_module.base_vector[4]))
