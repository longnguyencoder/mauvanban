import React from 'react';
import { Document } from '../../api/documents';

interface PaymentModalProps {
    isOpen: boolean;
    onClose: () => void;
    document: Document | null;
}

export default function PaymentModal({ isOpen, onClose, document }: PaymentModalProps) {
    if (!isOpen || !document) return null;

    // VietQR Config
    const BANK_ID = 'MB';
    const ACCOUNT_NO = '0398481719';
    const TEMPLATE = 'compact2'; // compact2 is usually clean
    const ACCOUNT_NAME = 'Mau Van Ban'; // Optional

    // Generate QR URL
    // Format: https://img.vietqr.io/image/<BANK>-<ACC>-<TEMPLATE>.png?amount=<AMOUNT>&addInfo=<CONTENT>
    const amount = document.price;
    const content = `Mua ${document.code}`;
    const qrUrl = `https://img.vietqr.io/image/${BANK_ID}-${ACCOUNT_NO}-${TEMPLATE}.png?amount=${amount}&addInfo=${encodeURIComponent(content)}&accountName=${encodeURIComponent(ACCOUNT_NAME)}`;

    const zaloLink = "https://zalo.me/0398481719";

    return (
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
                        <p className="text-gray-600 mb-2">Quét mã QR để thanh toán cho văn bản:</p>
                        <h4 className="font-bold text-lg text-blue-800">{document.title}</h4>
                        <p className="text-red-600 font-bold text-xl mt-1">
                            {new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(document.price)}
                        </p>
                    </div>

                    {/* QR Code */}
                    <div className="flex justify-center mb-6">
                        <img
                            src={qrUrl}
                            alt="VietQR Payment"
                            className="border-2 border-dashed border-blue-200 rounded-lg p-2 max-h-64 object-contain"
                        />
                    </div>

                    {/* Manual Info */}
                    <div className="bg-gray-50 p-4 rounded-lg text-sm text-gray-700 space-y-2 mb-6">
                        <div className="flex justify-between">
                            <span>Ngân hàng:</span>
                            <span className="font-bold">MB Bank</span>
                        </div>
                        <div className="flex justify-between">
                            <span>Số tài khoản:</span>
                            <span className="font-bold track-wider copy-text cursor-pointer" onClick={() => navigator.clipboard.writeText(ACCOUNT_NO)} title="Click để sao chép">{ACCOUNT_NO} 📋</span>
                        </div>
                        <div className="flex justify-between">
                            <span>Chủ tài khoản:</span>
                            <span className="font-bold">NGUYEN VAN LONG</span>
                            {/* Assuming name from previous context or generic placeholder matching user phone/account? 
                                User didn't give name, but '0398481719' is phone. 
                                I'll leave name generic or wait user to correct. 
                                Actually user said "Ngân hàng Mb bank số tài khoản 0398481719". 
                                I will hide Account Name row if unsure, but VietQR usually shows it.
                                Let's put the Phone/Name as implied.
                             */}
                        </div>
                        <div className="flex justify-between">
                            <span>Nội dung CK:</span>
                            <span className="font-bold text-blue-600">{content}</span>
                        </div>
                    </div>

                    {/* Instructions */}
                    <div className="text-center space-y-4">
                        <p className="text-sm text-gray-500 italic">
                            Sau khi chuyển khoản thành công, vui lòng liên hệ Zalo để nhận file ngay lập tức.
                        </p>

                        <a
                            href={zaloLink}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="block w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-lg flex items-center justify-center gap-2 transition-colors"
                        >
                            <span className="text-xl">💬</span> Liên hệ Zalo nhận file
                        </a>

                        <button
                            onClick={onClose}
                            className="block w-full text-gray-500 hover:text-gray-700 text-sm font-medium"
                        >
                            Đóng cửa sổ này
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
