import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import sqlite3
import datetime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class OnlineRetailApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Online Retail Application Management System")
        self.root.configure(bg="#f0f0f0")
        self.db_init()
        self.current_user = None
        self.cart = {}

        # Center the window
        window_width = 1000
        window_height = 600
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

        self.create_login_screen()
        self.add_default_products()

    def db_init(self):
        self.conn = sqlite3.connect("retail.db")
        self.cursor = self.conn.cursor()

        # Users: user_id (PK), username, password, role ('admin' or 'customer')
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin', 'customer'))
            )
        """)

        # Products: product_id (PK), name, price, stock_quantity
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                stock_quantity INTEGER NOT NULL
            )
        """)

        # Orders: order_id (PK), user_id (FK), order_date, total_amount, payment_status
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                order_date TEXT NOT NULL,
                total_amount REAL NOT NULL,
                payment_status TEXT NOT NULL CHECK(payment_status IN ('paid', 'pending')),
                FOREIGN KEY(user_id) REFERENCES users(user_id)
            )
        """)

        # OrderItems: id (PK), order_id (FK), product_id (FK), quantity, price_each
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                price_each REAL NOT NULL,
                FOREIGN KEY(order_id) REFERENCES orders(order_id),
                FOREIGN KEY(product_id) REFERENCES products(product_id)
            )
        """)
        self.conn.commit()

        # Ensure admin user exists with default credentials (admin/admin123)
        self.cursor.execute("SELECT * FROM users WHERE role='admin'")
        admin = self.cursor.fetchone()
        if not admin:
            self.cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                                ("admin", "admin123", "admin"))
            self.conn.commit()

    def add_default_products(self):
        self.cursor.execute("SELECT COUNT(*) FROM products")
        if self.cursor.fetchone()[0] == 0:
            default_products = [
                ("Laptop", 999.99, 50),
                ("Smartphone", 699.99, 100),
                ("Headphones", 149.99, 200),
                ("Tablet", 399.99, 75),
                ("Smartwatch", 199.99, 150)
            ]
            self.cursor.executemany(
                "INSERT INTO products (name, price, stock_quantity) VALUES (?, ?, ?)",
                default_products
            )
            self.conn.commit()

    def create_login_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.root.geometry("350x200")
        self.root.configure(bg="#f0f0f0")

        # Center the login window
        window_width = 350
        window_height = 200
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

        tk.Label(self.root, text="Online Retail Application", font=("Arial", 16), bg="#f0f0f0").pack(pady=10)
        tk.Label(self.root, text="Login", font=("Arial", 12), bg="#f0f0f0").pack(pady=5)

        tk.Label(self.root, text="Username", bg="#f0f0f0").pack()
        self.login_username = tk.Entry(self.root)
        self.login_username.pack()

        tk.Label(self.root, text="Password", bg="#f0f0f0").pack()
        self.login_password = tk.Entry(self.root, show="*")
        self.login_password.pack()

        tk.Button(self.root, text="Login", command=self.login, bg="#99ccff").pack(pady=5)
        tk.Button(self.root, text="Register as Customer", command=self.create_register_screen, bg="#99ff99").pack()
        tk.Button(self.root, text="Logout", command=self.logout, bg="#ff6666").pack(pady=5)

    def create_register_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.root.geometry("350x240")
        self.root.configure(bg="#f0f0f0")

        # Center the register window
        window_width = 350
        window_height = 240
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

        tk.Label(self.root, text="Register (Customer)", font=("Arial", 16), bg="#f0f0f0").pack(pady=10)

        tk.Label(self.root, text="Username", bg="#f0f0f0").pack()
        self.reg_username = tk.Entry(self.root)
        self.reg_username.pack()

        tk.Label(self.root, text="Password", bg="#f0f0f0").pack()
        self.reg_password = tk.Entry(self.root, show="*")
        self.reg_password.pack()

        tk.Label(self.root, text="Confirm Password", bg="#f0f0f0").pack()
        self.reg_confirm_password = tk.Entry(self.root, show="*")
        self.reg_confirm_password.pack()

        tk.Button(self.root, text="Register", command=self.register_customer, bg="#99ff99").pack(pady=10)
        tk.Button(self.root, text="Back to Login", command=self.create_login_screen, bg="#ffcc99").pack()
        tk.Button(self.root, text="Logout", command=self.logout, bg="#ff6666").pack(pady=5)

    def login(self):
        username = self.login_username.get().strip()
        password = self.login_password.get().strip()
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password.")
            return

        self.cursor.execute("SELECT user_id, role, password FROM users WHERE username=?", (username,))
        row = self.cursor.fetchone()
        if row and row[2] == password:
            self.current_user = {"user_id": row[0], "username": username, "role": row[1]}
            if row[1] == "admin":
                self.create_admin_dashboard()
            else:
                self.create_customer_dashboard()
        else:
            messagebox.showerror("Error", "Invalid username or password.")

    def register_customer(self):
        username = self.reg_username.get().strip()
        password = self.reg_password.get().strip()
        confirm_password = self.reg_confirm_password.get().strip()

        if not username or not password or not confirm_password:
            messagebox.showerror("Error", "Please fill all fields.")
            return
        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match.")
            return
        try:
            self.cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                                (username, password, "customer"))
            self.conn.commit()
            messagebox.showinfo("Success", "Registration successful! Please login.")
            self.create_login_screen()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists. Choose another.")

    def create_customer_dashboard(self):
        self.cart = {}
        for widget in self.root.winfo_children():
            widget.destroy()
        self.root.geometry("1000x600")
        self.root.configure(bg="#f0f0f0")

        header_frame = tk.Frame(self.root, bg="#f0f0f0")
        header_frame.pack(fill=tk.X, pady=5)
        tk.Label(header_frame, text=f"Welcome, {self.current_user['username']} (Customer)", 
                font=("Arial", 14), bg="#f0f0f0").pack(side=tk.LEFT, padx=10)
        btn_back = tk.Button(header_frame, text="Back", command=self.create_login_screen, bg="#ffcc99")
        btn_back.pack(side=tk.RIGHT, padx=5)
        btn_logout = tk.Button(header_frame, text="Logout", command=self.logout, bg="#ff6666")
        btn_logout.pack(side=tk.RIGHT, padx=5)

        # Main content frame
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Product list frame
        product_frame = tk.Frame(main_frame, bg="#e6f2ff", bd=2, relief=tk.GROOVE)
        product_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(product_frame, text="Available Products", font=("Arial", 12), bg="#e6f2ff").pack()

        self.product_tree = ttk.Treeview(product_frame, columns=("name", "price", "stock"), show="headings", height=20)
        self.product_tree.heading("name", text="Product Name")
        self.product_tree.heading("price", text="Price")
        self.product_tree.heading("stock", text="In Stock")
        self.product_tree.column("name", width=200, anchor=tk.W)
        self.product_tree.column("price", width=100, anchor=tk.CENTER)
        self.product_tree.column("stock", width=100, anchor=tk.CENTER)
        self.product_tree.pack(fill=tk.BOTH, expand=True)

        self.product_tree.bind("<Double-1>", self.add_product_to_cart_dialog)

        tk.Label(product_frame, text="Double-click a product to add to cart", bg="#e6f2ff").pack(pady=5)

        # Cart frame
        cart_frame = tk.Frame(main_frame, bg="#ffe6e6", bd=2, relief=tk.GROOVE)
        cart_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(cart_frame, text="Your Cart", font=("Arial", 12), bg="#ffe6e6").pack()
        self.cart_tree = ttk.Treeview(cart_frame, columns=("name", "quantity", "price_each", "total"), show="headings", height=15)
        self.cart_tree.heading("name", text="Product")
        self.cart_tree.heading("quantity", text="Quantity")
        self.cart_tree.heading("price_each", text="Price Each")
        self.cart_tree.heading("total", text="Total Price")
        self.cart_tree.column("name", width=150, anchor=tk.W)
        self.cart_tree.column("quantity", width=75, anchor=tk.CENTER)
        self.cart_tree.column("price_each", width=100, anchor=tk.CENTER)
        self.cart_tree.column("total", width=100, anchor=tk.CENTER)
        self.cart_tree.pack(fill=tk.BOTH, expand=True)

        btn_frame = tk.Frame(cart_frame, bg="#ffe6e6")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Remove Selected Item", command=self.remove_selected_cart_item, bg="#ff9999").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Place Order & Pay", command=self.place_order, bg="#99ff99").pack(side=tk.LEFT, padx=5)

        self.load_products()

    def load_products(self):
        for row in self.product_tree.get_children():
            self.product_tree.delete(row)
        self.cursor.execute("SELECT product_id, name, price, stock_quantity FROM products")
        for product_id, name, price, stock in self.cursor.fetchall():
            self.product_tree.insert("", tk.END, iid=str(product_id), 
                                  values=(name, f"${price:.2f}", stock))

    def add_product_to_cart_dialog(self, event):
        selected_item = self.product_tree.focus()
        if not selected_item:
            return
        product_id = int(selected_item)
        item_data = self.product_tree.item(selected_item)
        name = item_data['values'][0]
        price = float(item_data['values'][1].replace('$', ''))
        stock = int(item_data['values'][2])
        
        if stock <= 0:
            messagebox.showinfo("Out of Stock", f"The product '{name}' is out of stock.")
            return

        quantity = simpledialog.askinteger("Quantity", f"Enter quantity for '{name}' (max {stock}):", 
                                          minvalue=1, maxvalue=stock)
        if quantity is None:
            return

        if product_id in self.cart:
            new_qty = self.cart[product_id]["quantity"] + quantity
            if new_qty > stock:
                messagebox.showerror("Error", "Quantity exceeds available stock.")
                return
            self.cart[product_id]["quantity"] = new_qty
        else:
            self.cart[product_id] = {"name": name, "price": price, "quantity": quantity}
        self.load_cart()

    def load_cart(self):
        for row in self.cart_tree.get_children():
            self.cart_tree.delete(row)
        for pid, item in self.cart.items():
            total_price = item["price"] * item["quantity"]
            self.cart_tree.insert("", tk.END, iid=str(pid),
                                values=(item["name"], item["quantity"], 
                                       f"${item['price']:.2f}", f"${total_price:.2f}"))

    def remove_selected_cart_item(self):
        selected = self.cart_tree.focus()
        if not selected:
            messagebox.showinfo("Info", "Please select an item to remove.")
            return
        pid = int(selected)
        if pid in self.cart:
            del self.cart[pid]
            self.load_cart()

    def place_order(self):
        if not self.cart:
            messagebox.showerror("Error", "Your cart is empty.")
            return

        # Check stock availability again before placing order
        for pid, item in self.cart.items():
            self.cursor.execute("SELECT stock_quantity FROM products WHERE product_id=?", (pid,))
            stock = self.cursor.fetchone()[0]
            if item["quantity"] > stock:
                messagebox.showerror("Error", f"Insufficient stock for '{item['name']}'. Available: {stock}")
                return

        total_amount = sum(item["price"] * item["quantity"] for item in self.cart.values())
        confirm = messagebox.askyesno("Confirm Order", f"Total amount: ${total_amount:.2f}\nProceed to pay?")
        if not confirm:
            return

        # Insert order
        order_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute(
            "INSERT INTO orders (user_id, order_date, total_amount, payment_status) VALUES (?, ?, ?, ?)",
            (self.current_user["user_id"], order_date, total_amount, "paid"))
        order_id = self.cursor.lastrowid

        # Insert order items and update stock
        for pid, item in self.cart.items():
            self.cursor.execute(
                "INSERT INTO order_items (order_id, product_id, quantity, price_each) VALUES (?, ?, ?, ?)",
                (order_id, pid, item["quantity"], item["price"])
            )
            self.cursor.execute(
                "UPDATE products SET stock_quantity = stock_quantity - ? WHERE product_id = ?",
                (item["quantity"], pid)
            )

        self.conn.commit()
        messagebox.showinfo("Success", "Order placed and payment done successfully!")
        self.cart = {}
        self.load_cart()
        self.load_products()

    def create_admin_dashboard(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.root.geometry("1000x600")
        self.root.configure(bg="#f0f0f0")

        header_frame = tk.Frame(self.root, bg="#f0f0f0")
        header_frame.pack(fill=tk.X, pady=5)
        tk.Label(header_frame, text=f"Welcome, {self.current_user['username']} (Admin)", 
                font=("Arial", 14), bg="#f0f0f0").pack(side=tk.LEFT, padx=10)
        btn_back = tk.Button(header_frame, text="Back", command=self.create_login_screen, bg="#ffcc99")
        btn_back.pack(side=tk.RIGHT, padx=5)
        btn_logout = tk.Button(header_frame, text="Logout", command=self.logout, bg="#ff6666")
        btn_logout.pack(side=tk.RIGHT, padx=5)

        # Tab control for admin
        tab_control = ttk.Notebook(self.root)
        tab_control.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tab 1: Add product
        add_product_tab = ttk.Frame(tab_control)
        tab_control.add(add_product_tab, text="Add New Product")

        tk.Label(add_product_tab, text="Product Name").grid(row=0, column=0, pady=5, padx=10, sticky=tk.E)
        self.admin_prod_name = tk.Entry(add_product_tab, width=40)
        self.admin_prod_name.grid(row=0, column=1, pady=5, sticky=tk.W)

        tk.Label(add_product_tab, text="Price ($)").grid(row=1, column=0, pady=5, padx=10, sticky=tk.E)
        self.admin_prod_price = tk.Entry(add_product_tab, width=20)
        self.admin_prod_price.grid(row=1, column=1, pady=5, sticky=tk.W)

        tk.Label(add_product_tab, text="Stock Quantity").grid(row=2, column=0, pady=5, padx=10, sticky=tk.E)
        self.admin_prod_stock = tk.Entry(add_product_tab, width=20)
        self.admin_prod_stock.grid(row=2, column=1, pady=5, sticky=tk.W)

        tk.Button(add_product_tab, text="Add Product", command=self.admin_add_product, 
                 bg="#99ff99").grid(row=3, column=1, pady=10, sticky=tk.W)

        # Tab 2: View product sales statistics with graph
        stats_tab = ttk.Frame(tab_control)
        tab_control.add(stats_tab, text="Product Sales Statistics")

        # Create a frame for the graph
        graph_frame = tk.Frame(stats_tab)
        graph_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create a frame for the table
        table_frame = tk.Frame(stats_tab)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.stats_tree = ttk.Treeview(table_frame, columns=("total_quantity", "total_sales"), 
                                      show="headings", height=10)
        self.stats_tree.heading("total_quantity", text="Total Quantity Sold")
        self.stats_tree.heading("total_sales", text="Total Sales ($)")
        self.stats_tree.column("total_quantity", width=150, anchor=tk.CENTER)
        self.stats_tree.column("total_sales", width=150, anchor=tk.CENTER)
        self.stats_tree.pack(fill=tk.BOTH, expand=True)

        # Button to refresh statistics
        btn_refresh = tk.Button(stats_tab, text="Refresh Statistics", 
                              command=self.load_statistics, bg="#99ccff")
        btn_refresh.pack(pady=5)

        # Initialize graph
        self.figure = Figure(figsize=(8, 4), dpi=100)
        self.plot = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.load_statistics()

    def admin_add_product(self):
        name = self.admin_prod_name.get().strip()
        price_str = self.admin_prod_price.get().strip()
        stock_str = self.admin_prod_stock.get().strip()

        if not name or not price_str or not stock_str:
            messagebox.showerror("Error", "Please enter product name, price and stock quantity.")
            return
        try:
            price = float(price_str)
            stock = int(stock_str)
            if price < 0 or stock < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Price must be positive number and stock must be a positive integer.")
            return

        self.cursor.execute(
            "INSERT INTO products (name, price, stock_quantity) VALUES (?, ?, ?)",
            (name, price, stock)
        )
        self.conn.commit()
        messagebox.showinfo("Success", f"Product '{name}' added successfully!")
        self.admin_prod_name.delete(0, tk.END)
        self.admin_prod_price.delete(0, tk.END)
        self.admin_prod_stock.delete(0, tk.END)

    def load_statistics(self):
        # Clear existing data
        for row in self.stats_tree.get_children():
            self.stats_tree.delete(row)
        self.plot.clear()

        # Get sales statistics: total quantity sold and total sales per product
        self.cursor.execute("""
            SELECT p.name, 
                   IFNULL(SUM(oi.quantity), 0) AS total_quantity,
                   IFNULL(SUM(oi.quantity * oi.price_each), 0) AS total_sales
            FROM products p
            LEFT JOIN order_items oi ON p.product_id = oi.product_id
            GROUP BY p.name
            ORDER BY total_sales DESC
        """)
        stats_data = self.cursor.fetchall()
        
        if not stats_data:
            return

        # Prepare data for the table and graph
        product_names = []
        quantities = []
        sales = []
        
        for name, qty, sales_amount in stats_data:
            self.stats_tree.insert("", tk.END, values=(qty, f"${sales_amount:.2f}"), text=name)
            product_names.append(name)
            quantities.append(qty)
            sales.append(sales_amount)

        # Create bar graph
        x = range(len(product_names))
        bars = self.plot.bar(x, sales, color='skyblue')
        self.plot.set_title('Product Sales Performance')
        self.plot.set_xlabel('Products')
        self.plot.set_ylabel('Total Sales ($)')
        self.plot.set_xticks(x)
        self.plot.set_xticklabels(product_names, rotation=45, ha='right')
        
        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            self.plot.text(bar.get_x() + bar.get_width()/2., height,
                         f'${height:.2f}',
                         ha='center', va='bottom')

        self.figure.tight_layout()
        self.canvas.draw()

    def logout(self):
        self.current_user = None
        self.cart = {}
        self.create_login_screen()


if __name__ == "__main__":
    root = tk.Tk()
    app = OnlineRetailApp(root)
    root.mainloop()