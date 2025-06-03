# 先依照擁有食材數量從多到少排序，當擁有食材數量相同時，再依照缺少食材數量從少到多排序。

import json
import tkinter as tk
import tkinter.font as tkFont
import pandas as pd
import re
from tkinter import messagebox, font

########################################################################
# FlowFrame 實作：透過 place() 在父容器中動態換行排列多個 widget
########################################################################
class FlowFrame(tk.Frame):
    """
    一個自訂的 Flow Layout Frame，會依照容器寬度自動換行放置子元件。
    """
    def __init__(self, parent, margin=5, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self._margin = margin
        self._items = []
        self.bind("<Configure>", self._on_configure)

    def add_widget(self, widget):
        """
        將 widget 納入 FlowFrame 管理。
        """
        self._items.append(widget)
        widget.place(in_=self)

    def _on_configure(self, event):
        """
        監聽 FlowFrame 大小變化，動態重新排版子元件。
        """
        x, y = self._margin, self._margin
        line_height = 0
        avail_width = event.width
        for w in self._items:
            reqw = w.winfo_reqwidth()
            reqh = w.winfo_reqheight()
            if x + reqw + self._margin > avail_width:
                x = self._margin
                y += line_height + self._margin
                line_height = 0
            w.place(x=x, y=y)
            x += reqw + self._margin
            if reqh > line_height:
                line_height = reqh

# -------------------------------------------------------------
# 函式：讀取 Excel (食譜)
# -------------------------------------------------------------
def load_recipes_from_excel(excel_file='recipes.xlsx'):
    df = pd.read_excel(excel_file)
    recipes_list = []
    for _, row in df.iterrows():
        food_name = row['食物'] if not pd.isna(row['食物']) else "未提供"
        tags_str = row['標籤'] if not pd.isna(row['標籤']) else ""
        tags = [t.strip() for t in tags_str.split(',')] if tags_str else []
        ingredients_str = row['食材'] if not pd.isna(row['食材']) else ""
        ingredients = [ing.strip() for ing in ingredients_str.split('\n')] if ingredients_str else []
        steps_str = row['步驟'] if not pd.isna(row['步驟']) else ""
        steps = [s.strip() for s in steps_str.split('\n')] if steps_str else []
        servings = row['份量'] if not pd.isna(row['份量']) else "未提供"
        time_text = row['時間'] if not pd.isna(row['時間']) else "未提供"

        recipe_dict = {
            "食物": food_name,
            "標籤": tags,
            "食材": ingredients,
            "步驟": steps,
            "份量": servings,
            "時間": time_text
        }
        recipes_list.append(recipe_dict)
    return recipes_list

# -------------------------------------------------------------
# 新增：讀取 Excel (同義詞對照表)
# 格式假設為:
#  key    | synonyms
#  -------|----------------------------------
#  蒜頭   | 蒜頭, 蒜, 大蒜, 蒜瓣, 蒜末, 蒜泥
#  ...
# -------------------------------------------------------------
def load_synonyms_from_excel(synonym_file='synonyms.xlsx'):
    df = pd.read_excel(synonym_file)
    synonyms_map = {}
    for _, row in df.iterrows():
        # A 欄: key
        # B 欄: synonyms (以逗號分隔)
        if 'key' not in df.columns or 'synonyms' not in df.columns:
            continue  # 或 raise Exception("synonyms.xlsx 的欄位必須是 key, synonyms")

        key_val = str(row['key']).strip()
        synonyms_str = str(row['synonyms']).strip()
        if not key_val:
            continue
        
        # 以逗號切分，並 strip 每個詞
        syn_list = [x.strip() for x in synonyms_str.split(',') if x.strip()]
        synonyms_map[key_val] = syn_list
    
    return synonyms_map

# -------------------------------------------------------------
# 函式：計算匹配度
# -------------------------------------------------------------
def compute_recommended(user_input, recipes, synonyms_map):
    user_input = user_input.strip()
    if not user_input:
        return []

    user_ingredients = user_input.split()
    matched_ingredients = set()

    for ui in user_ingredients:
        ui_lower = ui.lower()
        found_match = False
        # 在 synonyms_map 中比對
        for key, synonyms in synonyms_map.items():
            # 如果 ui_lower 在該 key 的同義詞清單裡（忽略大小寫）
            if ui_lower in [s.lower() for s in synonyms]:
                matched_ingredients.add(key)
                found_match = True
                break
        if not found_match:
            # 沒在任何同義詞清單裡，直接把 ui 當成一個獨立食材關鍵字
            matched_ingredients.add(ui)

    recommended = []
    for recipe in recipes:
        have_count = 0
        need_count = 0
        missing_ings = []

        recipe_ings = []
        for ing in recipe["食材"]:
            parts = ing.split()
            ing_name = parts[0] if parts else ing
            recipe_ings.append(ing_name)

        for r_ing in recipe_ings:
            r_ing_lower = r_ing.lower()
            matched = any(m.lower() in r_ing_lower for m in matched_ingredients)
            if matched:
                have_count += 1
            else:
                need_count += 1
                missing_ings.append(r_ing)

        recommended.append({
            "recipe": recipe,
            "have_count": have_count,
            "need_count": need_count,
            "missing_ings": missing_ings,
        })

    return recommended

# -------------------------------------------------------------
# 顯示「詳細」視窗
# (與主要頁面相似的 Canvas + Frame + Scrollbar)
# -------------------------------------------------------------
def show_detail(recipe, have_count, need_count):
    detail_win = tk.Toplevel()
    detail_win.title("詳細資訊")
    detail_win.geometry("950x650")

    container = tk.Frame(detail_win)
    container.pack(fill='both', expand=True)

    vscrollbar = tk.Scrollbar(container, orient="vertical")
    vscrollbar.pack(side=tk.RIGHT, fill='y')

    canvas = tk.Canvas(container, yscrollcommand=vscrollbar.set)
    canvas.pack(side=tk.LEFT, fill='both', expand=True)
    vscrollbar.config(command=canvas.yview)

    detail_frame = tk.Frame(canvas)
    canvas_window = canvas.create_window((0, 0), window=detail_frame, anchor='nw')

    detail_labels = []  # 用來做動態換行

    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
        new_width = event.width - 20
        if new_width < 1:
            new_width = 1
        for lbl in detail_labels:
            lbl.config(wraplength=new_width)

    detail_frame.bind("<Configure>", on_frame_configure)

    def on_canvas_configure(event):
        canvas.itemconfig(canvas_window, width=event.width)
    canvas.bind("<Configure>", on_canvas_configure)

    def _on_detail_mousewheel(event):
        if event.delta:
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        elif event.num == 4:
            canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            canvas.yview_scroll(1, "units")

    detail_win.bind("<MouseWheel>", _on_detail_mousewheel)
    detail_win.bind("<Button-4>", _on_detail_mousewheel)
    detail_win.bind("<Button-5>", _on_detail_mousewheel)

    # 幫手函式: 建立 Label 並加入 detail_labels
    def add_label(parent, text, font_=None, fg_=None, pady=0):
        lbl = tk.Label(
            parent,
            text=text,
            font=font_,
            fg=fg_,
            anchor="w",
            justify="left",
            wraplength=1  # 初始設為 1，待畫面更新後由 <Configure> 動態調整
        )
        lbl.pack(fill='x', padx=10, pady=pady)
        detail_labels.append(lbl)
        return lbl

    # ----------------- 以下依照原先內容插入 --------------------
    add_label(detail_frame, recipe['食物'], ("微軟正黑體", 22, "bold"), "DodgerBlue2", pady=(10,5))

    # 標籤
    tags_str = ", ".join(recipe["標籤"]) if recipe["標籤"] else ""
    if tags_str:
        add_label(detail_frame, tags_str, ("微軟正黑體", 16, "bold"), "DeepSkyBlue2", pady=(0,10))

    # 份量與時間合併成同一行，中間隔3個空格，保留各自顏色
    if recipe['份量'] != "未提供" or recipe['時間'] != "未提供":
        qty_time_frame = tk.Frame(detail_frame)
        qty_time_frame.pack(fill='x', pady=(0,10))
        if recipe['份量'] != "未提供":
            lbl_qty = tk.Label(qty_time_frame,
                               text=f"  份量: {recipe['份量']}",
                               font=("微軟正黑體", 18, "bold"),
                               fg="DarkOrchid1",
                               anchor="w",
                               justify="left",
                               wraplength=1)
            lbl_qty.pack(side=tk.LEFT)
            detail_labels.append(lbl_qty)
        # 中間加3個空格
        spacer = tk.Label(qty_time_frame,
                          text="   ",
                          font=("微軟正黑體", 18, "bold"),
                          fg="black",
                          anchor="w",
                          justify="left",
                          wraplength=1)
        spacer.pack(side=tk.LEFT)
        detail_labels.append(spacer)
        if recipe['時間'] != "未提供":
            lbl_time = tk.Label(qty_time_frame,
                                text=f"時間: {recipe['時間']}",
                                font=("微軟正黑體", 18, "bold"),
                                fg="dark orchid",
                                anchor="w",
                                justify="left",
                                wraplength=1)
            lbl_time.pack(side=tk.LEFT)
            detail_labels.append(lbl_time)

    # ★ 在份量與時間區塊與食材區塊之間加入空白行
    add_label(detail_frame, "", ("微軟正黑體", 10), "black")

    # 食材
    ing_line_frame = tk.Frame(detail_frame)
    ing_line_frame.pack(fill='x', pady=(0,5))

    lbl1 = tk.Label(
        ing_line_frame,
        text="  食材(",
        font=("微軟正黑體", 18, "bold"),
        fg="violet red",
        anchor='w',
        justify='left',
        wraplength=1
    )
    lbl1.pack(side=tk.LEFT)
    detail_labels.append(lbl1)

    lbl2 = tk.Label(
        ing_line_frame,
        text=f"擁有{have_count}",
        font=("微軟正黑體", 18, "bold"),
        fg="lime green",
        anchor='w',
        justify='left',
        wraplength=1
    )
    lbl2.pack(side=tk.LEFT)
    detail_labels.append(lbl2)

    lbl3 = tk.Label(
        ing_line_frame,
        text=f" 缺少{need_count}",
        font=("微軟正黑體", 18, "bold"),
        fg="firebrick1",
        anchor='w',
        justify='left',
        wraplength=1
    )
    lbl3.pack(side=tk.LEFT)
    detail_labels.append(lbl3)

    lbl4 = tk.Label(
        ing_line_frame,
        text="):",
        font=("微軟正黑體", 18, "bold"),
        fg="violet red",
        anchor='w',
        justify='left',
        wraplength=1
    )
    lbl4.pack(side=tk.LEFT)
    detail_labels.append(lbl4)

    for i, ing in enumerate(recipe["食材"], start=1):
        add_label(detail_frame, f"{i}. {ing}", ("微軟正黑體", 14, "bold"), "gray10")

    # 若不需要額外空白行可移除下面這行
    add_label(detail_frame, "", ("微軟正黑體", 10), "black")

    # 食物詳細步驟
    add_label(detail_frame, "食物詳細步驟:", ("微軟正黑體", 18, "bold"), "dark orange", pady=(10,5))
    for i, step_text in enumerate(recipe["步驟"], start=1):
        add_label(detail_frame, f"{i}. {step_text}", ("微軟正黑體", 14, "bold"), "gray10", pady=(0,5))

# -------------------------------------------------------------
# 主介面顯示結果
# -------------------------------------------------------------
def display_results(recommended, results_frame):
    for widget in results_frame.winfo_children():
        widget.destroy()

    if not recommended:
        tk.Label(results_frame, text="目前沒有可顯示的結果，請先搜尋。").pack(pady=10)
        return

    for idx, item in enumerate(recommended):
        recipe = item["recipe"]
        have_count = item["have_count"]
        need_count = item["need_count"]
        missing_ings = item["missing_ings"]
        missing_str = ", ".join(missing_ings) if missing_ings else "（無缺少食材）"

        item_frame = tk.Frame(results_frame, bd=1, relief="solid")
        item_frame.pack(fill='x', pady=5, padx=5)

        first_line_frame = tk.Frame(item_frame)
        first_line_frame.pack(fill='x', pady=(5,0))

        food_label = tk.Label(
            first_line_frame,
            text=f"[{idx+1}] {recipe['食物']}",
            font=("微軟正黑體", 16, "bold"),
            fg="DodgerBlue2",
            wraplength=1,
            anchor='w',
            justify='left'
        )
        food_label.pack(side=tk.LEFT, fill='x', expand=True, padx=(10,0))

        detail_btn = tk.Button(
            first_line_frame, text="詳細資訊",
            command=lambda r=recipe, h=have_count, n=need_count: show_detail(r, h, n)
        )
        detail_btn.pack(side=tk.RIGHT, padx=10)

        have_label = tk.Label(
            item_frame,
            text=f"擁有食材數量: {have_count}",
            font=("微軟正黑體", 14, "bold"),
            fg="lime green",
            wraplength=1,
            anchor='w',
            justify='left'
        )
        have_label.pack(anchor='w', padx=20)

        need_label = tk.Label(
            item_frame,
            text=f"缺少食材數量: {need_count}",
            font=("微軟正黑體", 14, "bold"),
            fg="firebrick1",
            wraplength=1,
            anchor='w',
            justify='left'
        )
        need_label.pack(anchor='w', padx=20)

        missing_label = tk.Label(
            item_frame,
            text=f"缺少的食材細項: {missing_str}",
            font=("微軟正黑體", 14, "bold"),
            fg="gray10",
            wraplength=1,
            anchor='w',
            justify='left'
        )
        missing_label.pack(anchor='w', padx=20, pady=(0,5))

        def on_item_frame_configure(event, labels):
            new_width = event.width - 20
            if new_width < 1:
                new_width = 1
            for lbl in labels:
                lbl.config(wraplength=new_width)

        item_frame.bind(
            "<Configure>",
            lambda e, labs=(food_label, have_label, need_label, missing_label): on_item_frame_configure(e, labs)
        )

# -------------------------------------------------------------
# 主程式
# -------------------------------------------------------------
def main():
    window = tk.Tk()
    window.title("食材運用推薦系統")
    window.geometry("950x650")
    window.option_add("*Font", "微軟正黑體 14")

    # 1) 讀取食譜 Excel
    recipes = load_recipes_from_excel('recipes.xlsx')
    # 2) 讀取同義詞對照表 Excel
    synonyms_map = load_synonyms_from_excel('synonyms.xlsx')

    recommended_data = []

    # 上方輸入區
    top_frame = tk.Frame(window)
    top_frame.pack(pady=10)

    tk.Label(top_frame, text="請輸入目前擁有的食材（以空格分隔）：").pack()

    line2_frame = tk.Frame(top_frame)
    line2_frame.pack(pady=5)

    input_entry = tk.Entry(line2_frame, width=40)
    input_entry.pack(side=tk.LEFT, padx=5)

    def do_match():
        user_input = input_entry.get().strip()
        if not user_input:
            messagebox.showwarning("警告", "請輸入至少一項食材！")
            return
        nonlocal recommended_data

        # 1) 先計算匹配度
        recommended_data = compute_recommended(user_input, recipes, synonyms_map)

        # 2) 多鍵排序
        recommended_data.sort(key=lambda x: (-x['have_count'], x['need_count']))

        # 3) **僅保留前 100 筆結果**
        recommended_data = recommended_data[:100]

        # 4) 顯示結果
        display_results(recommended_data, results_frame)

    tk.Button(line2_frame, text="開始搜尋", command=do_match).pack(side=tk.LEFT, padx=5)

    # 可捲動區 (主要頁面)
    container = tk.Frame(window)
    container.pack(fill='both', expand=True)

    vscrollbar = tk.Scrollbar(container, orient="vertical")
    vscrollbar.pack(side=tk.RIGHT, fill='y')

    canvas = tk.Canvas(container, yscrollcommand=vscrollbar.set)
    canvas.pack(side=tk.LEFT, fill='both', expand=True)
    vscrollbar.config(command=canvas.yview)

    results_frame = tk.Frame(canvas)
    canvas_window = canvas.create_window((0, 0), window=results_frame, anchor='nw')

    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    results_frame.bind("<Configure>", on_frame_configure)

    def on_canvas_configure(event):
        canvas.itemconfig(canvas_window, width=event.width)
    canvas.bind("<Configure>", on_canvas_configure)

    def _on_main_mousewheel(event):
        if event.delta:
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        elif event.num == 4:
            canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            canvas.yview_scroll(1, "units")

    window.bind("<MouseWheel>", _on_main_mousewheel)
    window.bind("<Button-4>", _on_main_mousewheel)
    window.bind("<Button-5>", _on_main_mousewheel)

    window.mainloop()

if __name__ == "__main__":
    main()
