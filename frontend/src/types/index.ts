export interface Product {
  id: number;
  name: string;
  sku: string;
  price: string;
  quantity: number;
  created_at: string;
  updated_at: string;
}

export interface Customer {
  id: number;
  full_name: string;
  email: string;
  phone: string;
  created_at: string;
}

export interface OrderItem {
  id: number;
  product_id: number;
  product_name: string;
  quantity: number;
  unit_price: string;
  subtotal: string;
}

export interface Order {
  id: number;
  customer_id: number;
  customer: Customer;
  status: string;
  total_amount: string;
  created_at: string;
  items: OrderItem[];
}

export interface Dashboard {
  total_products: number;
  total_customers: number;
  total_orders: number;
  low_stock_count: number;
  low_stock_products: Product[];
}
