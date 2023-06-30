import tkinter as tk
from tkinter import messagebox
import random
import gc
import os
import time
import threading

#----------------------------------------------------------------------------------
# Code cho nút Solve
#----------------------------------------------------------------------------------
# Hàm giải
def solve_button():
    global depth_limit,stop_flag
    stop_flag = True
    depth_limit = 1000000   #cài đặt độ sâu tìm kiếm, giới hạn thời gian giải, tránh treo ứng dụng
    for row in range(9):    #các ô phục hồi về size chuẩn là 20
        for col in range(9):
            entries[row][col].config(font=("Arial",20))
    solve()                 # gọi hàm solve
    
# Code giải Sudoku chính
def solve():
    # kiểm tra không hợp lệ truoc khi giải để tiết kiệm thời gian giải, tránh treo ứng dụng khi không giải được
    for row in range(9):
        for col in range(9):
            num = board[row][col]
            if num != 0:
                if not is_valid(row, col, num):
                    status_label.config(text=status[1],foreground="red")
                    return False
    # gọi hàm solve_sudoku để giải
    if solve_sudoku():
        update_entries()    #cap nhat giá trị cho các ô, mới hien thị duoc
        status_label.config(text=status[0],foreground="black")
        return True
    else:
        status_label.config(text=status[1],foreground="red")
        return False

# Code giải Sudoku lõi
def solve_sudoku():

    # kiểm tra hết ô trống xem như giải xong
    if not find_empty_cell():
        return True
    
    #kiểm tra đạt độ sâu tìm kiếm hay chưa, nếu đúng thì dừng lại, không tìm tiếp
    if limit():
        status_label.config(text=status[1],foreground="red")
        return False
        
    # Tìm ô chưa được điền
    row, col = find_empty_cell()

    for num in range(1, 10):
        if is_valid(row, col, num):
            board[row][col] = num
            if solve_sudoku():     # Gọi đệ quy
                return True
            board[row][col] = 0  # Quay lui nếu không tìm được lời giải

    return False

# giới hạn độ sâu tìm kiếm để dừng lại khi đạt đến giới hạn
def limit():
    global depth_limit
    depth_limit-=1         #mỗi thao tác độ sâu bị trừ 1
    if depth_limit <= 0:   #đạt độ sâu tìm kiếm thì dừng lại
        return True
    else:
        return False
    
# Code tìm ô trống
def find_empty_cell():
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                return row, col
    return None

# Code kiểm tra tính hợp lệ
def is_valid(row, col, num):
    for i in range(9):
        if board[row][i] == num and i != col:  #duyet hang ngang, trừ vị trí hiện tại
            return False

    for i in range(9):
        if board[i][col] == num and i != row:  #duyet hang doc, trừ vị trí hiện tại
            return False

    start_row = (row // 3) * 3   #duyet nhóm 3x3, trừ vị trí hiện tại
    start_col = (col // 3) * 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num and (start_row + i != row or start_col + j != col):
                return False

    return True

# Code cập nhật giá trị nhập liệu
def update_entries():
    for row in range(9):
        for col in range(9):
            entries[row][col].delete(0, tk.END)
            entries[row][col].insert(0, str(board[row][col]))          
            
#----------------------------------------------------------------------------------
# Code cho nút xóa
#----------------------------------------------------------------------------------
            
# hàm xóa toàn bộ, dùng cho nút clear all
def clear():
    global is_note,stop_flag,is_first
    is_note=False
    is_first=True
    stop_flag = True
    for row in range(9):
        for col in range(9):
            #xoa toan bo du lieu
            board[row][col] = 0
            note_str[row][col] = ""
            entries[row][col].delete(0, tk.END)
    status_label.config(text="Code By: Trần Quốc Minh",foreground="black")
    time1_label.config(text="00:00")
    time2_label.config(text="00:00")
    display_relax()   #gọi lại phần hiển thị mới

#Hàm thiết lập lại đề sudoku ban đầu, dùng cho nut nhan play again
def reset():
    global is_note,stop_flag
    global stop_flag, time_thread, lock
    is_note=False
    for row in range(9):
        for col in range(9):
            note_str[row][col] = ""
            #cập nhật lại đề ban đầu
            board[row][col] = relax[row][col] 
    status_label.config(text="Code By: Trần Quốc Minh",foreground="black")
    time1_label.config(text="00:00")
    time2_label.config(text="00:00")
    display_relax()   #gọi lại phần hiển thị mới

    with lock:
        stop_flag = True
        if time_thread is not None:
            time_thread.join()
        stop_flag = False
        time_thread = threading.Thread(target=update_label)
        time_thread.start()  # Bắt đầu đếm giờ 
        is_first=False
# hàm xóa từng kí tự, cho nút nhấn del
def delete():
    if selected_entry:
        if not is_note:
            write_number("")
        else:
            cursor_pos = selected_entry.index("insert")  # Lấy vị trí hiện tại của con trỏ
            selected_entry.delete(cursor_pos - 1, cursor_pos)  # Xóa phía trước con trỏ
            validate_cell()  # Gọi hàm validate_cell() để kiểm tra ô đầu vào

#----------------------------------------------------------------------------------
#Code cho các nút nhập số từ 1 đến 9
#----------------------------------------------------------------------------------
# Hàm ghi số, dùng cho các nút từ 1 đến 9, và nút del
def write_number(number):
    # Ghi số tương ứng vào vị trí đang chọn ô của grid
    if selected_entry:
        key_number()
        selected_entry.insert(len(selected_entry.get()),number)
        validate_cell()  # Gọi hàm validate_cell() để kiểm tra ô đầu vào
# hàm xác định vị trí ô đang chọn, đồng thòi cập nhật size cho chế độ thường và ghi chú        
def select_entry(entry):
    global selected_entry
    selected_entry = entry
    note_exe()
    
# hàm cho phép ghi nhieu so vao một o trong che do ghi chú
# trong che do thuong, size được phục hồi lại ban đầu
def key_number():
    if not is_note:
        selected_entry.delete(0, tk.END)
        selected_entry.insert(0, "")
        selected_entry.config(font=("Arial",20))
    else:
        selected_entry.config(font=("Arial",10))
        
#----------------------------------------------------------------------------------
# Code liên quan đến việc ghi chú
#----------------------------------------------------------------------------------
                
#ham khi nhấn nút ghi chú
def note():
    global is_note
    is_note=not is_note
    note_exe()

#ham xu li ghi chú, chỉnh size nhỏ khi ghi chú,size lớn khi không ghi chú
#cho các ô trống, các số có gia tri không bị thay đổi
def note_exe():
    for row in range(9):
        for col in range(9):
            entry=entries[row][col]
            if selected_entry==entry and entry.get()=="":
                if is_note:
                    entry.config(font=("Arial",10))
                else:
                    entry.config(font=("Arial",20))        

#----------------------------------------------------------------------------------
# Code liên quan đến việc kiểm tra giá trị hợp lệ khi nhập
#----------------------------------------------------------------------------------

# Code kiểm tra tính hợp lệ của giá trị nhập vào (1 đến 9, và phím xóa)
def validate_input(value):
    if value.isdigit() and int(value) % 10 != 0 or value == "" or value == "\x08":  # Xử lý phím xóa (ASCII code: 0x08)):
        return True
    else:
        return False
           
# Code tô màu các giá trị nhập vào: xanh: đúng, đỏ: sai, trắng: không có giá trị
def validate_cell():
    global stop_flag
    if not is_note:
        for row in range(9):
            for col in range(9):
                value = entries[row][col].get()
                if value.isdigit() and 1 <= int(value) <= 9:
                    board[row][col] = int(value)
                else:
                    board[row][col] = 0
                    if selected_entry==entries[row][col] and note_str[row][col] != "":
                        entries[row][col].insert(0,note_str[row][col])
                        entries[row][col].config(font=("Arial",10))
    else:
        for row in range(9):
            for col in range(9):
                entry = entries[row][col]
                if selected_entry==entry:
                    board[row][col] = 0
                    note_str[row][col]=entry.get()
                    entry.config(bg="white")


    # kiểm tra không hợp lệ truoc khi giải
    for row in range(9):
        for col in range(9):
            num = board[row][col]
            if num != 0:
                if is_valid(row, col, num):
                    entries[row][col].config(bg="light green")  # Tô nền màu xanh nhạt cho ô hợp lệ
                else:
                    entries[row][col].config(bg="red")  # Thiết lập màu nền mặc định (trắng) cho ô không hợp lệ
            else:
                entries[row][col].config(bg="white")  # Thiết lập màu nền mặc định (trắng) cho ô không phải số
     # ---------
    try:
        for row in range(9):
            for col in range(9):
                if "" == board[row][col]:
                    raise StopIteration
        for row in range(9):
            for col in range(9):
                num = board[row][col]
                if not is_valid(row, col, num):
                    raise StopIteration
        stop_flag = True
        messagebox.showinfo(victory[0], victory[1])
    except StopIteration:
        pass


#----------------------------------------------------------------------------------
# Code cho nut Relax
#----------------------------------------------------------------------------------

# hàm chính của nút relax
def random_sudoku():
    global depth_limit,relax,level
    global stop_flag, time_thread, lock

    #-------------------------------------------------------------------------------
    #1. xóa toàn bộ dữ liệu trong bảng 9x9
    #2. lấy ngẫu nhiên 10 số từ 0 đến 9, xếp vào ngẫu nhiên vị trí trong bảng 9x9
    #3. giải bài sudoku với các vị trí ở bước 2
    #4. xóa ngẫu nhiên một số vị trí trong bảng 9x9
    #5. cập nhật dữ liệu cho các ô
    #6. hiển thị
    #7. luu đề sudoku
    #8. hien thi thoi gian
    #-------------------------------------------------------------------------------
    while True:
        clear()             # xoa toan bo du lieu
        random_number(10)   # giới hạn độ đa dạng
        depth_limit = 5000  # giới hạn độ sâu tìm kiếm
        if solve() or not limit():
            break
    random_clear(level)    #mac dinh 50 vị trí được xóa, có thể thay đổi để thay đổi độ khó
    update_entries()   
    display_relax()
    for row in range(9):
        for col in range(9):
            relax[row][col] = board[row][col]
    #khoi chay dong ho dem
    with lock:
        stop_flag = True
        if time_thread is not None:
            time_thread.join()
        stop_flag = False
        time_thread = threading.Thread(target=update_label)
        time_thread.start()  # Bắt đầu đếm giờ 
# hàm lấy ngẫu nhiên 'number' số từ 0 đến 9, xếp vào ngẫu nhiên vị trí trong bảng 9x9
def random_number(number):
    datas = [1, 2, 3, 4, 5, 6, 7, 8, 9]

    for _ in range(number):
        data = random.choice(datas)
        while True:
            row = random.randint(0, 8)
            col = random.randint(0, 8)
            if board[row][col] == 0:
                break
        # kiểm tra hợp lệ (không trùng hàng, cột, ô 3x3) thì mới lấy giá trị đó
        if is_valid(row, col, data):
            board[row][col] = data

# hàm xóa ngẫu nhiên một số vị trí trong bảng 9x9
def random_clear(number):
    for _ in range(number):
        while True:
            row = random.randint(0, 8)
            col = random.randint(0, 8)
            if board[row][col] != 0:
                board[row][col] = 0
                break

    status_label.config(text="Code By: Trần Quốc Minh",foreground="black")

# hàm hiển thị các câu đó sudoku trong chế độ " relax "
def display_relax():
    for row in range(9):
        for col in range(9):
            value = board[row][col]
            if value != 0:
                # Hiển thị giá trị của ô đã biết
                entry = tk.Entry(window, width=2, font=("Arial", 20), justify="center")
                entry.insert(tk.END, str(value))
                entry.grid(row=row, column=col, sticky="nsew")
                entry.config(bg="yellow")  # Tô nền màu vàng cho đề bài sudoku
                entry.bind("<Button-1>", disable_entry) # Vô hiệu hóa sự kiện click chuột để người dùng không xóa, sửa được đế bài sudoku

            else:
                # Hiển thị ô trống
                entry = tk.Entry(window, width=2, font=("Arial", 20), justify="center")
                entry.grid(row=row, column=col, sticky="nsew")

                # Cung cấp các sự kiện và logic để nhập giá trị vào từng ô
                entry.config(validate="key", validatecommand=(entry.register(validate_input), "%P"))  #sự kiện nhập từ bàn phím
                entry.bind("<Key>", lambda event, r=row, c=col: key_number()) # Đính kèm sự kiện change
                entry.bind("<KeyRelease>", lambda event, r=row, c=col: validate_cell())  # sự kiện thay đổi nội dung trong ô, gọi hàm validate_cell()
                entry.bind("<Button-1>", lambda event, e=entry: select_entry(e))  # sự kiện click chuột trái, gọi hàm select_entry(e)
                

                entries[row][col] = entry
            
            # Kẻ viền cho nhóm 3x3
            if row == 2 or row == 5:
                entry.grid(pady=(0, 3))
            if col == 2 or col == 5:
                entry.grid(padx=(0, 3))

# hàm ngắt sự kiện, tránh trường hợp người dùng sửa đề bài sudoku
def disable_entry(event):
    return "break"  

# hàm tính thoi gian
def update_label():
    global stop_flag
    start_time = time.time()
    while not stop_flag:
        elapsed_time = time.time() - start_time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        formatted_time = f"{minutes:02d}:{seconds:02d}"
        time1_label.config(text=formatted_time)
        time2_label.config(text=formatted_time)
        time.sleep(1)  # Delay 1 giây

#----------------------------------------------------------------------------------
# Code liên quan đến việc chọn và hiển thị cấp độ chơi
#----------------------------------------------------------------------------------
#giam do kho
def level_a():
    global level
    if level > 35:
        level-=5
    level_status()
    
#tang do kho
def level_d():
    global level
    if level <= 60:
        level+=5
    level_status()
    
#hien thi thong bao
def level_status():
    if level <40:
        level_label.config(text=lev[0])
    elif level <45:
        level_label.config(text=lev[1])
    elif level <50:
        level_label.config(text=lev[2])
    elif level <55:
        level_label.config(text=lev[3])       
    elif level <60:
        level_label.config(text=lev[4])
    elif level <65:
        level_label.config(text=lev[5])        
    else:
        level_label.config(text=lev[6])
        
#----------------------------------------------------------------------------------
# Code cho nút Exit
#----------------------------------------------------------------------------------
# Code thoát ứng dụng            
def quit_app():
    global stop_flag
    stop_flag = True
    window.destroy()
    
# Xử lý khi nút "Close" được nhấn
def handle_close():
    quit_app()
#----------------------------------------------------------------------------------
# Code cho nút chuyển ngôn ngữ
#----------------------------------------------------------------------------------
# Hàm chuyển đổi ngôn ngữ
def change_language(event):
    

    if selected_language[0] == "Tiếng Việt":
        window.title("Sudoku Solver")
        solve_button.config(text="Solve")
        clear_button.config(text="Clear All")
        relax_button.config(text="Relax")
        quit_button.config(text="Exit")
        note_button.config(text="Note")        
        reset_button.config(text="Play Again")
        del_button.config(text="Del")
        victory[0] = "Info"
        victory[1] = "Victory...!!! 1000 likes....!!!"
        language_label.config(text="---> Tiếng Việt")
        status[0]="Sudoku solved successfully!"
        status[1]="No solution found for Sudoku."     
        selected_language[0] = "English"
        for i in range(7):
            lev[i]=lev_en[i]
        level_status()
    else:
        window.title("Giải Sudoku")
        solve_button.config(text="Giải")
        clear_button.config(text="Xóa Hết")
        relax_button.config(text="Thư giãn")
        quit_button.config(text="Thoát")
        note_button.config(text="Ghi chú")        
        reset_button.config(text="Chơi Lại")
        del_button.config(text="Xóa")
        victory[0] = "Thông báo"
        victory[1] = "Chiến thắng...!!! 1000 likes....!!!"
        language_label.config(text="---> English")
        status[0]="Sudoku được giải!"
        status[1]="Không tìm thấy giải pháp cho Sudoku."
        selected_language[0] = "Tiếng Việt"
        for i in range(7):
            lev[i]=lev_vi[i]
        level_status()


#----------------------------------------------------------------------------------
# Code hiển thị chính ban đầu 
#----------------------------------------------------------------------------------
# hàm hiển thị chính
def display_main():  
    for row in range(9):
        entry_row = []
        for col in range(9):
            entry = tk.Entry(window, width=5, font=("Arial", 20), justify="center")
            entry.grid(row=row, column=col, sticky="nsew")
            entry.config(validate="key", validatecommand=(entry.register(validate_input), "%P"))
            entry.bind("<Key>", lambda event, r=row, c=col: key_number()) # Đính kèm sự kiện change
            entry.bind("<Button-1>", lambda event, e=entry: select_entry(e))  # Gọi hàm select_entry khi người dùng nhấp chuột vào ô
            entry.bind("<KeyRelease>", lambda event, r=row, c=col: validate_cell()) # Đính kèm sự kiện change
#             entry.bind("<Button-1>", get_cell_value)
            
            entry_row.append(entry)

            # Kẻ viền cho nhóm 3x3
            if row == 2 or row == 5:
                entry.grid(pady=(0, 3))
            if col == 2 or col == 5:
                entry.grid(padx=(0, 3))
        entries.append(entry_row)

#----------------------------------------------------------------------------------
# Code Khởi tạo giao diện cho ứng dụng
#----------------------------------------------------------------------------------
# hàm Khởi tạo cửa sổ ứng dụng
def interface():
    # khai bao bien toan cuc
    global window,solve_button,clear_button,quit_button,relax_button,status_label,language_label,\
    del_button,reset_button,note_button,level_label,time1_label,time2_label
    
    # khởi tạo cửa sổ giao diện
    window = tk.Tk()
    # Đăng ký hàm xử lý khi cửa sổ đóng
    window.protocol("WM_DELETE_WINDOW", handle_close)
    
    window.title("Sudoku Solver")
    window.configure(bg="black")  # Đặt màu nền của cửa sổ là màu đen
    
    # Đặt kích thước mặc định cho cửa sổ
    window.geometry("600x700")  # Thay đổi kích thước theo nhu cầu của bạn
    
    try:
        # Lấy đường dẫn thư mục của script hiện tại
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # Đường dẫn tới tệp tin icon (ví dụ: icon.ico) tương đối với thư mục hiện tại
        icon_filename = "sudoku.ico"
        icon_path = os.path.join(current_dir, icon_filename)

        # Kiểm tra xem tệp tin icon có tồn tại không
        if os.path.exists(icon_path):
            # Đặt biểu tượng cho cửa sổ nếu tệp tin icon tồn tại
            window.iconbitmap(icon_path)
    except:
        pass
    # Định dạng cửa sổ ứng dụng đầy khung cửa sổ
    for i in range(9):
        window.grid_columnconfigure(i, weight=1)
        window.grid_rowconfigure(i, weight=1)
    window.grid_rowconfigure(9, weight=1)
    window.grid_rowconfigure(10, weight=1)
       
    # Nút giải Sudoku
    solve_button = tk.Button(window, text="Solve", command=solve_button)
    solve_button.grid(row=9, column=0, columnspan=1, sticky="nsew")
    solve_button.config(bg="cyan")

    # Nút thư giãn
    relax_button = tk.Button(window, text="Relax", command=random_sudoku)
    relax_button.grid(row=9, column=1, columnspan=1, sticky="nsew")
    
    # Nút ghi chú
    note_button = tk.Button(window, text="Note", command=note)
    note_button.grid(row=9, column=2, columnspan=1, sticky="nsew")
    
    # Nút thiết lập lại
    reset_button = tk.Button(window, text="Play Again", command=reset)
    reset_button.grid(row=9, column=3, columnspan=3, sticky="nsew")
    
    # Nút delete
    del_button = tk.Button(window, text="Del", command=delete)
    del_button.grid(row=9, column=6, columnspan=1, sticky="nsew")
    
    # Nút xóa het
    clear_button = tk.Button(window, text="Clear All", command=clear)
    clear_button.grid(row=9, column=7, columnspan=1, sticky="nsew")

    # Nút thoát
    quit_button = tk.Button(window, text="Exit", command=quit_app)
    quit_button.grid(row=9, column=8, columnspan=1, sticky="nsew")
    quit_button.config(bg="orange")  

    #các nút số  
    one_button = tk.Button(window, text="1", command=lambda: write_number(1))
    one_button.config(bg="light blue",font=("Arial", 18))  # Đặt màu nền của nút lệnh là màu xanh nhạt
    one_button.grid(row=11, column=0, columnspan=1, sticky="nsew")

    two_button = tk.Button(window, text="2", command=lambda: write_number(2))
    two_button.config(bg="light blue",font=("Arial", 18))
    two_button.grid(row=11, column=1, columnspan=1, sticky="nsew")

    three_button = tk.Button(window, text="3", command=lambda: write_number(3))
    three_button.config(bg="light blue",font=("Arial", 18))
    three_button.grid(row=11, column=2, columnspan=1, sticky="nsew")

    four_button = tk.Button(window, text="4", command=lambda: write_number(4))
    four_button.config(bg="light blue",font=("Arial", 18))
    four_button.grid(row=11, column=3, columnspan=1, sticky="nsew")

    five_button = tk.Button(window, text="5", command=lambda: write_number(5))
    five_button.config(bg="light blue",font=("Arial", 18))
    five_button.grid(row=11, column=4, columnspan=1, sticky="nsew")

    six_button = tk.Button(window, text="6", command=lambda: write_number(6))
    six_button.config(bg="light blue",font=("Arial", 18))
    six_button.grid(row=11, column=5, columnspan=1, sticky="nsew")

    seven_button = tk.Button(window, text="7", command=lambda: write_number(7))
    seven_button.config(bg="light blue",font=("Arial", 18))
    seven_button.grid(row=11, column=6, columnspan=1, sticky="nsew")

    eight_button = tk.Button(window, text="8", command=lambda: write_number(8))
    eight_button.config(bg="light blue",font=("Arial", 18))
    eight_button.grid(row=11, column=7, columnspan=1, sticky="nsew")

    nine_button = tk.Button(window, text="9", command=lambda: write_number(9))
    nine_button.config(bg="light blue",font=("Arial", 18))
    nine_button.grid(row=11, column=8, columnspan=1, sticky="nsew") 
    
    # trạng thái level
    level_label = tk.Label(window, text="Hard")
    level_label.grid(row=10, column=0, columnspan=9, sticky="nsew")
    level_label.config(bg="light green",font=("Arial", 12), justify="center")
    
    # Nút giảm độ khó
    back_button = tk.Button(window, text="<----", command=level_a)
    back_button.grid(row=10, column=1, columnspan=2, sticky="nsew")
    back_button.config(bg="cyan")
    
    # Nút tang độ khó
    next_button = tk.Button(window, text="---->", command=level_d)
    next_button.grid(row=10, column=6, columnspan=2, sticky="nsew")
    next_button.config(bg="orange")
    
    # dem gio
    time1_label = tk.Label(window,text = "00:00",foreground="red")
    time1_label.grid(row=10,column=0,columnspan=1,sticky="nsew")
    time1_label.config(font=("Arial", 14,"bold"), justify="center")
   
   # dem gio
    time2_label = tk.Label(window,text = "00:00",foreground="red")
    time2_label.grid(row=10,column=8,columnspan=1,sticky="nsew")
    time2_label.config(font=("Arial", 14,"bold"), justify="center")   
    
    # thanh trạng thái
    status_label = tk.Label(window, text="Code By: Trần Quốc Minh")
    status_label.grid(row=12, column=0, columnspan=9, sticky="nsew")
    
    # chuyển đổi ngôn ngữ
    language_label = tk.Label(window, text="---> Tiếng Việt")
    language_label.grid(row=12, column=7, columnspan=2, sticky="nsew")
    language_label.bind("<Button-1>", change_language)       # Ràng buộc sự kiện nhấp chuột trái, gọi hàm change_language

#----------------------------------------------------------------------------------
# Code chương trình chính
#----------------------------------------------------------------------------------

# khởi tạo các biến ban đầu
selected_language = ["English"]
status =["Sudoku solved successfully!","No solution found for Sudoku."]
victory = ["Info","Victory...!!! 1000 likes...."]
lev_en = ["Intro","Easy","Medium","Hard","Expert","Final boss","Universe" ]
lev_vi = ["Nhập môn","Dễ","Trung bình","Khó","Chuyên gia","Trùm cuối","Tầm vũ trụ" ]
lev =  ["Intro","Easy","Medium","Hard","Expert","Final boss","Universe" ]
selected_entry = None  # Khởi tạo biến selected_entry để kiểm tra ô có đang được chọn hay không
entries = []    #dùng để luu giá trị entry của ô
relax = [[0] * 9 for _ in range(9)]  # Khởi tạo biến relax để luu đề
board = [[0] * 9 for _ in range(9)]  # Khởi tạo biến board để chứa các giá trị trong ô
note_str = [[""] * 9 for _ in range(9)] #chua thong tin ghi chú
is_note=False   #kiểm tra chế độ ghi chú
level = 50    #mức độ khó của sudoku
#----hien thi thoi gian--------
stop_flag = True
time_thread = None
lock = threading.Lock()
#--------------------------------
# gọi các hàm
interface()       # giao diện
display_main()    # chuong trình chính
gc.collect()  # Giải phóng bộ nhớ
# Chạy giao diện trên luồng chính
window.mainloop() # lặp ứng dụng






