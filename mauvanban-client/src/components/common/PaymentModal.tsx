import { useState } from 'react';
import { Document } from '../../api/documents';
import { QrCodeIcon } from '@heroicons/react/24/outline';
import SepayPaymentModal from '../SepayPaymentModal';

interface PaymentModalProps {
    isOpen: boolean;
    onClose: () => void;
    document: Document | null;
    onSuccess?: () => void;
}

export default function PaymentModal({ isOpen, onClose, document, onSuccess }: PaymentModalProps) {
    const [isSepayOpen, setIsSepayOpen] = useState(false);

    if (!isOpen || !document) return null;

    // VietQR Config (Manual Fallback)
    // SePay QR Config (Manual Fallback)
    // SePay QR Config (Manual Fallback)
    const acc = '9924666';
    const bank = 'ACB';
    const amount = document.price;
    const des = document.code; // Description: MVB-XXXXX

    // https://qr.sepay.vn/img?acc=LOCSPAY000324416&bank=ACB&amount=100000&des=Mua MVB-123
    const qrUrl = `https://qr.sepay.vn/img?acc=${acc}&bank=${bank}&amount=${amount}&des=${encodeURIComponent(des)}`;
    const zaloLink = "https://zalo.me/0398481719";

    const handleSepaySuccess = () => {
        setIsSepayOpen(false);
        if (onSuccess) onSuccess();
    };

    return (
        <>
            <SepayPaymentModal
                isOpen={isSepayOpen}
                onClose={() => setIsSepayOpen(false)}
                itemType="document"
                itemId={document.id}
                onSuccess={handleSepaySuccess}
            />

            <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50">
                <div className="bg-white rounded-xl shadow-2xl max-w-md w-full overflow-hidden animate-fadeIn">

                    {/* Header */}
                    <div className="bg-blue-600 p-4 text-white flex justify-between items-center">
                        <h3 className="text-xl font-bold">Thanh toán & Nhận file</h3>
                        <button onClick={onClose} className="text-white hover:text-gray-200 text-2xl">&times;</button>
                    </div>

                    {/* Body */}
                    <div className="p-6">
                        <div className="text-center mb-6">
                            <p className="text-gray-600 mb-2">Giá bán tài liệu:</p>
                            <h4 className="font-bold text-lg text-blue-800">{document.title}</h4>
                            <p className="text-red-600 font-bold text-2xl mt-1">
                                {new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(document.price)}
                            </p>
                        </div>

                        {/* Options */}
                        <div className="space-y-4">
                            {/* Auto Payment Option (SePay) */}
                            <button
                                onClick={() => setIsSepayOpen(true)}
                                className="w-full bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-700 hover:to-primary-800 text-white font-bold py-4 px-4 rounded-xl flex items-center justify-center gap-3 shadow-lg transform transition-transform hover:scale-[1.02]"
                            >
                                <QrCodeIcon className="w-8 h-8" />
                                <div className="text-left">
                                    <div className="text-lg">Thanh toán Tự Động</div>
                                    <div className="text-xs text-primary-100 font-normal">Nhận file ngay lập tức (Khuyên dùng)</div>
                                </div>
                            </button>

                            <div className="relative flex py-2 items-center">
                                <div className="flex-grow border-t border-gray-300"></div>
                                <span className="flex-shrink mx-4 text-gray-400 text-sm">Hoặc chuyển khoản thủ công</span>
                                <div className="flex-grow border-t border-gray-300"></div>
                            </div>

                            {/* Manual QR - Accordion or just secondary display */}
                            <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                                <div className="flex justify-between items-center mb-4">
                                    <span className="font-bold text-gray-700">QR Code Thủ Công</span>
                                    <span className="text-xs bg-gray-200 text-gray-600 px-2 py-1 rounded">Chậm hơn</span>
                                </div>

                                <div className="flex flex-col items-center">
                                    <img src={qrUrl} alt="VietQR" className="w-32 h-32 mb-2 rounded border" />
                                    <p className="text-xs text-gray-500 text-center mb-3">
                                        Nội dung: <span className="font-bold text-red-500">{des}</span>
                                    </p>
                                    <a
                                        href={zaloLink}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="text-blue-600 hover:text-blue-800 text-sm font-bold flex items-center gap-1"
                                    >
                                        <span>💬</span> Liên hệ Zalo để xác nhận
                                    </a>
                                </div>
                            </div>
                        </div>

                        <div className="mt-6 text-center">
                            <button
                                onClick={onClose}
                                className="text-gray-400 hover:text-gray-600 text-sm"
                            >
                                Đóng cửa sổ
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </>
    );
}
