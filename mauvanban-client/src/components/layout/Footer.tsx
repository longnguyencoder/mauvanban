export default function Footer() {
    return (
        <footer className="bg-gray-900 text-gray-300 pt-16 pb-8 border-t border-gray-800">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-12 mb-12">
                    <div className="col-span-1 md:col-span-1">
                        <h3 className="text-white text-lg font-bold mb-4 uppercase tracking-wider">Mẫu Văn Bản</h3>
                        <p className="text-sm leading-relaxed mb-4 text-gray-400">
                            Hệ thống cung cấp biểu mẫu, văn bản hành chính, pháp luật hàng đầu Việt Nam. Giúp bạn tiết kiệm thời gian và công sức.
                        </p>
                        <div className="flex gap-4">
                            {/* Social Icons Placeholders */}
                            <div className="w-8 h-8 bg-gray-700 rounded-full flex items-center justify-center hover:bg-primary-600 transition cursor-pointer">f</div>
                            <div className="w-8 h-8 bg-gray-700 rounded-full flex items-center justify-center hover:bg-primary-600 transition cursor-pointer">in</div>
                            <div className="w-8 h-8 bg-gray-700 rounded-full flex items-center justify-center hover:bg-primary-600 transition cursor-pointer">yt</div>
                        </div>
                    </div>

                    <div>
                        <h3 className="text-white text-sm font-bold mb-4 uppercase">Về chúng tôi</h3>
                        <ul className="space-y-2 text-sm">
                            <li><a href="#" className="hover:text-white transition">Giới thiệu</a></li>
                            <li><a href="#" className="hover:text-white transition">Tuyển dụng</a></li>
                            <li><a href="#" className="hover:text-white transition">Chính sách bảo mật</a></li>
                            <li><a href="#" className="hover:text-white transition">Điều khoản sử dụng</a></li>
                        </ul>
                    </div>

                    <div>
                        <h3 className="text-white text-sm font-bold mb-4 uppercase">Hỗ trợ</h3>
                        <ul className="space-y-2 text-sm">
                            <li><a href="#" className="hover:text-white transition">Hướng dẫn thanh toán</a></li>
                            <li><a href="#" className="hover:text-white transition">Quy định tải tài liệu</a></li>
                            <li><a href="#" className="hover:text-white transition">Câu hỏi thường gặp</a></li>
                            <li><a href="#" className="hover:text-white transition">Liên hệ quảng cáo</a></li>
                        </ul>
                    </div>

                    <div>
                        <h3 className="text-white text-sm font-bold mb-4 uppercase">Liên hệ</h3>
                        <ul className="space-y-3 text-sm">
                            <li className="flex items-start gap-3">
                                <span>📍</span>
                                <span>281/2/1 Bình Lợi, phường Bình Lợi Trung, TP. Hồ Chí Minh</span>
                            </li>
                            <li className="flex items-start gap-3">
                                <span>📞</span>
                                <span className="text-white font-bold">0398.481.719</span>
                            </li>
                            <li className="flex items-start gap-3">
                                <span>✉️</span>
                                <span>hotro@mauvanban.vn</span>
                            </li>
                        </ul>
                    </div>
                </div>

                <div className="border-t border-gray-800 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
                    <p className="text-sm text-gray-500">
                        &copy; 2025 Bản quyền thuộc về Mẫu Văn Bản.
                    </p>
                    <div className="flex items-center gap-2">
                        <span className="text-xs text-gray-600">Secure Payment:</span>
                        <div className="w-8 h-5 bg-gray-700 rounded"></div>
                        <div className="w-8 h-5 bg-gray-700 rounded"></div>
                        <div className="w-8 h-5 bg-gray-700 rounded"></div>
                    </div>
                </div>
            </div>
        </footer>
    );
}
