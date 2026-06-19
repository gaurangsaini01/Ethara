import { api } from "./client";
import type { Product } from "../types";

export interface ProductInput {
  name: string;
  sku: string;
  price: number;
  quantity: number;
}

export async function listProducts(): Promise<Product[]> {
  const { data } = await api.get<Product[]>("/products");
  return data;
}

export async function createProduct(input: ProductInput): Promise<Product> {
  const { data } = await api.post<Product>("/products", input);
  return data;
}

export async function updateProduct(id: number, input: ProductInput): Promise<Product> {
  const { data } = await api.put<Product>(`/products/${id}`, input);
  return data;
}

export async function deleteProduct(id: number): Promise<void> {
  await api.delete(`/products/${id}`);
}
