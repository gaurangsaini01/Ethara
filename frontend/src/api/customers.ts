import { api } from "./client";
import type { Customer } from "../types";

export interface CustomerInput {
  full_name: string;
  email: string;
  phone: string;
}

export async function listCustomers(): Promise<Customer[]> {
  const { data } = await api.get<Customer[]>("/customers");
  return data;
}

export async function createCustomer(input: CustomerInput): Promise<Customer> {
  const { data } = await api.post<Customer>("/customers", input);
  return data;
}

export async function deleteCustomer(id: number): Promise<void> {
  await api.delete(`/customers/${id}`);
}
