import { Fragment, useEffect, useState, useRef } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import { QrCodeIcon, CheckCircleIcon, XCircleIcon, ClockIcon } from '@heroicons/react/24/outline';
import { sepayApi, PaymentInfo, PaymentStatus } from '../api/sepay';
import { toast } from 'react-hot-toast';

interface SepayPaymentModalProps {
    isOpen: boolean;
    onClose: () => void;
    itemType: 'document' | 'package';
    itemId: string;
    onSuccess: () => void;
}

export default function SepayPaymentModal({
    isOpen,
    onClose,
    itemType,
    itemId,
    onSuccess
}: SepayPaymentModalProps) {
    const [isLoading, setIsLoading] = useState(true);
    const [paymentInfo, setPaymentInfo] = useState<PaymentInfo | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [status, setStatus] = useState<'pending' | 'completed' | 'failed' | 'cancelled'>('pending');
    const [timeLeft, setTimeLeft] = useState<number>(900); // 15 minutes

    // Polling interval
    const intervalRef = useRef<NodeJS.Timeout | null>(null);

    // Initial load - create payment request
    useEffect(() => {
        if (isOpen && itemId) {
            createPayment();
        }

        return () => {
            stopPolling();
        };
    }, [isOpen, itemId]);

    // Timer effect
    useEffect(() => {
        if (!isOpen || status !== 'pending') return;

        const timer = setInterval(() => {
            setTimeLeft((prev) => {
                if (prev <= 1) {
                    clearInterval(timer);
                    setStatus('failed');
                    setError('Payment expired');
                    return 0;
                }
                return prev - 1;
            });
        }, 1000);

        return () => clearInterval(timer);
    }, [isOpen, status]);

    const createPayment = async () => {
        try {
            setIsLoading(true);
            setError(null);

            const { data } = await sepayApi.createPayment({
                item_type: itemType,
                item_id: itemId
            });

            setPaymentInfo(data.data);
            startPolling(data.data.transaction_id);

            // Calculate time left based on expires_at
            const expiresAt = new Date(data.data.expires_at).getTime();
            const now = new Date().getTime();
            const secondsLeft = Math.floor((expiresAt - now) / 1000);
            setTimeLeft(secondsLeft > 0 ? secondsLeft : 0);

        } catch (err: any) {
            setError(err.response?.data?.message || 'Failed to generate payment request');
        } finally {
            setIsLoading(false);
        }
    };

    const startPolling = (transactionId: string) => {
        stopPolling();

        intervalRef.current = setInterval(async () => {
            try {
                const { data } = await sepayApi.checkStatus(transactionId);

                if (data.data.payment_status === 'completed') {
                    setStatus('completed');
                    stopPolling();
                    toast.success('Thanh toán thành công!');
                    setTimeout(() => {
                        onSuccess();
                        onClose();
                    }, 2000);
                } else if (data.data.payment_status === 'failed' || data.data.payment_status === 'cancelled') {
                    setStatus(data.data.payment_status);
                    stopPolling();
                    setError('Thanh toán thất bại hoặc đã bị hủy');
                }
            } catch (err) {
                console.error('Polling error', err);
            }
        }, 3000); // Poll every 3 seconds
    };

    const stopPolling = () => {
        if (intervalRef.current) {
            clearInterval(intervalRef.current);
            intervalRef.current = null;
        }
    };

    const handleCopy = (text: string) => {
        navigator.clipboard.writeText(text);
        toast.success('Đã sao chép!');
    };

    const formatTime = (seconds: number) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    const formatCurrency = (amount: number) => {
        return new Intl.NumberFormat('vi-VN', {
            style: 'currency',
            currency: 'VND'
        }).format(amount);
    };

    return (
        <Transition appear show={isOpen} as={Fragment}>
            <Dialog as="div" className="relative z-50" onClose={() => { }}>
                <Transition.Child
                    as={Fragment}
                    enter="ease-out duration-300"
                    enterFrom="opacity-0"
                    enterTo="opacity-100"
                    leave="ease-in duration-200"
                    leaveFrom="opacity-100"
                    leaveTo="opacity-0"
                >
                    <div className="fixed inset-0 bg-black bg-opacity-25" />
                </Transition.Child>

                <div className="fixed inset-0 overflow-y-auto">
                    <div className="flex min-h-full items-center justify-center p-4 text-center">
                        <Transition.Child
                            as={Fragment}
                            enter="ease-out duration-300"
                            enterFrom="opacity-0 scale-95"
                            enterTo="opacity-100 scale-100"
                            leave="ease-in duration-200"
                            leaveFrom="opacity-100 scale-100"
                            leaveTo="opacity-0 scale-95"
                        >
                            <Dialog.Panel className="w-full max-w-md transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all">
                                <div className="flex justify-between items-center mb-4">
                                    <Dialog.Title as="h3" className="text-lg font-medium leading-6 text-gray-900 flex items-center">
                                        <QrCodeIcon className="h-6 w-6 mr-2 text-primary-600" />
                                        Thanh toán QR Code
                                    </Dialog.Title>
                                    <button onClick={onClose} className="text-gray-400 hover:text-gray-500">
                                        <span className="sr-only">Close</span>
                                        <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                        </svg>
                                    </button>
                                </div>

                                {isLoading ? (
                                    <div className="flex justify-center items-center py-12">
                                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
                                    </div>
                                ) : error ? (
                                    <div className="text-center py-8">
                                        <XCircleIcon className="h-16 w-16 text-red-500 mx-auto mb-4" />
                                        <p className="text-red-500 mb-4">{error}</p>
                                        <button
                                            onClick={createPayment}
                                            className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
                                        >
                                            Thử lại
                                        </button>
                                    </div>
                                ) : status === 'completed' ? (
                                    <div className="text-center py-8">
                                        <CheckCircleIcon className="h-16 w-16 text-green-500 mx-auto mb-4" />
                                        <h3 className="text-xl font-bold text-green-600 mb-2">Thanh toán thành công!</h3>
                                        <p className="text-gray-600">Đang chuyển hướng...</p>
                                    </div>
                                ) : (
                                    <div className="space-y-6">
                                        {/* QR Code Section */}
                                        <div className="flex flex-col items-center justify-center bg-gray-50 p-4 rounded-xl border border-gray-200">
                                            <div className="text-sm font-medium text-gray-500 mb-2 flex items-center">
                                                <ClockIcon className="h-4 w-4 mr-1" />
                                                Hết hạn sau: <span className="text-red-600 ml-1 font-bold">{formatTime(timeLeft)}</span>
                                            </div>
                                            {paymentInfo?.qr_code && (
                                                <img
                                                    src={paymentInfo.qr_code}
                                                    alt="Payment QR Code"
                                                    className="w-48 h-48 object-contain mb-2 border-4 border-white shadow-sm rounded-lg"
                                                />
                                            )}
                                            <p className="text-xs text-gray-400">Sử dụng App ngân hàng để quét mã QR</p>
                                        </div>

                                        {/* Payment Details */}
                                        <div className="space-y-4">
                                            <div className="flex justify-between items-center p-3 bg-blue-50 rounded-lg border border-blue-100">
                                                <span className="text-sm text-gray-600">Số tiền:</span>
                                                <span className="text-xl font-bold text-blue-700">{formatCurrency(paymentInfo?.amount || 0)}</span>
                                            </div>

                                            <div className="space-y-3">
                                                <div className="flex justify-between items-center text-sm">
                                                    <span className="text-gray-500">Ngân hàng:</span>
                                                    <span className="font-medium text-gray-900">{paymentInfo?.bank_name}</span>
                                                </div>
                                                <div className="flex justify-between items-center text-sm">
                                                    <span className="text-gray-500">Số tài khoản:</span>
                                                    <div className="flex items-center">
                                                        <span className="font-medium text-gray-900 mr-2">{paymentInfo?.bank_account}</span>
                                                        <button
                                                            onClick={() => handleCopy(paymentInfo?.bank_account || '')}
                                                            className="text-primary-600 hover:text-primary-700 text-xs"
                                                        >
                                                            Sao chép
                                                        </button>
                                                    </div>
                                                </div>
                                                <div className="flex justify-between items-center text-sm">
                                                    <span className="text-gray-500">Chủ tài khoản:</span>
                                                    <span className="font-medium text-gray-900">{paymentInfo?.account_name}</span>
                                                </div>
                                                <div className="flex justify-between items-center text-sm bg-yellow-50 p-2 rounded border border-yellow-100">
                                                    <span className="text-gray-500">Nội dung CK:</span>
                                                    <div className="flex items-center">
                                                        <span className="font-bold text-red-600 mr-2">{paymentInfo?.content}</span>
                                                        <button
                                                            onClick={() => handleCopy(paymentInfo?.content || '')}
                                                            className="text-primary-600 hover:text-primary-700 text-xs"
                                                        >
                                                            Sao chép
                                                        </button>
                                                    </div>
                                                </div>
                                            </div>

                                            <div className="text-xs text-center text-gray-500 mt-4">
                                                <p>Hệ thống sẽ tự động xác nhận thanh toán sau khi bạn chuyển khoản thành công.</p>
                                            </div>
                                        </div>
                                    </div>
                                )}
                            </Dialog.Panel>
                        </Transition.Child>
                    </div>
                </div>
            </Dialog>
        </Transition>
    );
}
