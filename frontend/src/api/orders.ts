import { api } from "./client";
import type { Order } from "../types";

export interface OrderItemInput {
  product_id: number;
  quantity: number;
}

export interface OrderInput {
  customer_id: number;
  items: OrderItemInput[];
}

export async function listOrders(): Promise<Order[]> {
  const { data } = await api.get<Order[]>("/orders");
  return data;
}

export async function getOrder(id: number): Promise<Order> {
  const { data } = await api.get<Order>(`/orders/${id}`);
  return data;
}

export async function createOrder(input: OrderInput): Promise<Order> {
  const { data } = await api.post<Order>("/orders", input);
  return data;
}

export async function deleteOrder(id: number): Promise<void> {
  await api.delete(`/orders/${id}`);
}
