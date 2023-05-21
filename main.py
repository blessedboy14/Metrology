import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from help_methods import *
from sub_main import *


class MyWindow:
    def __init__(self):
        # window
        def _onKeyRelease(event):
            ctrl = (event.state & 0x4) != 0
            if event.keycode == 88 and ctrl and event.keysym.lower() != "x":
                event.widget.event_generate("<<Cut>>")

            if event.keycode == 86 and ctrl and event.keysym.lower() != "v":
                event.widget.event_generate("<<Paste>>")

            if event.keycode == 67 and ctrl and event.keysym.lower() != "c":
                event.widget.event_generate("<<Copy>>")

        self.window = tk.Tk()
        self.window.resizable(width=False, height=False)
        self.window.bind_all("<Key>", _onKeyRelease, "+")
        self.window.title("JSParser")
        self.window.geometry("1050x720")
        center(self.window)

        # styles
        self.frame_style = ttk.Style()
        self.frame_style.configure("My.TFrame", background="gray")

        # up frame
        self.panelFrame = ttk.Frame(self.window, height=30, style="My.TFrame")
        self.panelFrame.configure()

        # label
        self.info_label = ttk.Label(text="Текст программы на языке JavaScript: ", width=45)
        self.spen_lbl = ttk.Label(text="Метрики СПЕН")
        self.chepin_main_lbl = ttk.Label(text="Полная метрика Чепина")
        self.chepin_io_lbl = ttk.Label(text="Метрика Чепина ввода-вывода")

        # buttons
        self.do_btn = ttk.Button(self.window, text="Расчет метрик", takefocus=False)
        self.loadBtn = ttk.Button(self.panelFrame, text='Load', takefocus=False)

        # Entry and Text
        self.text_input = tk.Text(self.window, width=30, wrap="word", )
        self.spen_txt = tk.Text(self.window, wrap="word",)
        self.chepin_main_txt = tk.Text(self.window, width=30, wrap="word", )
        self.chepin_io_txt = tk.Text(self.window, width=30, wrap="word", )

    # binding funcs

    def Quit(self, ev):
        self.window.destroy()

    def LoadFile(self, ev):
        fn = filedialog.Open(self.window, filetypes=[('*.txt files', '.txt .js')]).show()
        if fn == '':
            return
        else:
            self.text_input.delete("1.0", tk.END)
            self.text_input.insert("1.0", open(fn, "rt").read())

    def make_pretty_output(self, a_complexity, operators_num, r_complexity, max_bl):
        main_metrics = f"Абсолютная сложность: {a_complexity}\nОтносительная сложность: " \
                       f"{a_complexity}/{operators_num}={r_complexity:.3f}"
        extended_metrics = f"Максимальный уровень вложенности: {max_bl}"
        return main_metrics, extended_metrics

    def calculate_all_metrics(self, ev):
        if len(self.text_input.get("0.0", tk.END)) == 0:
            return
        program_text = self.text_input.get("0.0", tk.END)
        spens_result, chepins_result, io_chepins_result = get_program_info(program_text)
        spens_str = ""
        sum = 0
        for value in spens_result:
            identifier, n = value
            spens_str += f"{identifier} : {n}\n"
            sum += n
        spens_str+= f"{sum}"
        chepins_str = "P: {\n"
        p_num = 0
        for value in chepins_result[VariableType.P]:
            chepins_str += f"{value},"
            p_num += 1
        chepins_str += "}\nM: {\n"
        m_num = 0
        for value in chepins_result[VariableType.M]:
            chepins_str += f"{value},"
            m_num += 1
        chepins_str += "}\nC: {\n"
        c_num = 0
        for value in chepins_result[VariableType.C]:
            chepins_str += f"{value},"
            c_num += 1
        chepins_str += "}\nT: {\n"
        t_num = 0
        for value in chepins_result[VariableType.T]:
            chepins_str += f"{value},"
            t_num += 1
        chepins_str += "}\n"
        chepin_value = 1*p_num + 2*m_num + 3*c_num + 0.5*t_num
        chepins_str += f"Value : 1*{p_num} + 2*{m_num} + 3*{c_num} + 0.5*{t_num} = {chepin_value}"
        self.spen_txt.delete("0.0", tk.END)
        self.chepin_main_txt.delete("0.0", tk.END)
        self.chepin_io_txt.delete("0.0", tk.END)
        self.spen_txt.insert("0.0", spens_str)
        self.chepin_main_txt.insert("0.0", chepins_str)
        chepins_str = "P: {\n"
        p_num = 0
        for value in io_chepins_result[VariableType.P]:
            chepins_str += f"{value},"
            p_num += 1
        chepins_str += "}\nM: {\n"
        m_num = 0
        for value in io_chepins_result[VariableType.M]:
            chepins_str += f"{value},"
            m_num += 1
        chepins_str += "}\nC: {\n"
        c_num = 0
        for value in io_chepins_result[VariableType.C]:
            chepins_str += f"{value},"
            c_num += 1
        chepins_str += "}\nT: {\n"
        t_num = 0
        for value in io_chepins_result[VariableType.T]:
            chepins_str += f"{value},"
            t_num += 1
        chepins_str += "}\n"
        chepin_value = 1 * p_num + 2 * m_num + 3 * c_num + 0.5 * t_num
        chepins_str += f"Value : 1*{p_num} + 2*{m_num} + 3*{c_num} + 0.5*{t_num} = {chepin_value}"
        self.chepin_io_txt.insert("0.0", chepins_str)

    # tkinter methods to bind it all together

    def binding(self):
        self.loadBtn.bind("<Button-1>", self.LoadFile)
        self.do_btn.bind("<Button-1>", self.calculate_all_metrics)

    def placing(self):
        self.text_input.place(x=15, y=70, height=640, width=350)
        self.spen_txt.place(x=610, y=70, height=150, width=415)
        self.spen_lbl.place(x=610, y=45, height=22)
        self.chepin_main_txt.place(x=610, y=265, height=200, width=415)
        self.chepin_main_lbl.place(x=610, y=240, height=22)
        self.chepin_io_txt.place(x=610, y=510, height=200, width=415)
        self.chepin_io_lbl.place(x=610, y=485, height=22)
        self.do_btn.place(x=410, y=70, width=150, height=50)
        self.panelFrame.pack(side='top', fill='x')
        self.loadBtn.place(x=10, y=3, width=40, height=22)
        self.info_label.place(x=15, y=45, height=22)
        self.info_label.config(font=("", 12))

    def run(self):
        self.window.mainloop()


class Main:
    def __init__(self):
        self.window = MyWindow()
        self.window.binding()
        self.window.placing()

    def main(self):
        self.window.run()


if __name__ == '__main__':
    myMain = Main()
    myMain.main()
