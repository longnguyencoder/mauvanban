import api from './axios';

export interface PaymentInfo {
    bank_account: string;
    bank_name: string;
    account_name: string;
    amount: number;
    content: string;
    transaction_id: string;
    qr_code: string;
    expires_at: string;
}

export interface PaymentStatus {
    transaction_id: string;
    payment_status: 'pending' | 'completed' | 'failed' | 'cancelled';
    amount: number;
    sepay_transaction_id?: string;
}

export const sepayApi = {
    // Create payment
    createPayment: (data: { item_type: 'document' | 'package'; item_id: string }) =>
        api.post<{ success: boolean; data: PaymentInfo }>('/sepay/create', data),

    // Check payment status
    checkStatus: (transactionId: string) =>
        api.get<{ success: boolean; data: PaymentStatus }>(`/sepay/check/${transactionId}`),

    // Cancel payment
    cancelPayment: (transactionId: string) =>
        api.post<{ success: boolean; message: string }>(`/sepay/cancel/${transactionId}`, {}),
};
