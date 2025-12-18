import { Routes, Route } from 'react-router-dom';
import { useEffect } from 'react';
import { useAuthStore } from './store/authStore';
import { Toaster } from 'react-hot-toast';

// Pages
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Documents from './pages/Documents';
import DocumentDetail from './pages/DocumentDetail';
import Categories from './pages/Categories';
import Profile from './pages/Profile';
import Contact from './pages/Contact';

// Admin Pages
import AdminLayout from './components/layout/AdminLayout';
import Dashboard from './pages/admin/Dashboard';
import DocumentList from './pages/admin/documents/DocumentList';
import CreateDocument from './pages/admin/documents/CreateDocument';
import EditDocument from './pages/admin/documents/EditDocument';
import CategoryList from './pages/admin/categories/CategoryList';
import CreateCategory from './pages/admin/categories/CreateCategory';
import UserList from './pages/admin/users/UserList';
import EditUser from './pages/admin/users/EditUser';

import CreateUser from './pages/admin/users/CreateUser';

// Layout
import Header from './components/layout/Header';
import Footer from './components/layout/Footer';

function App() {
    const loadUser = useAuthStore((state) => state.loadUser);

    useEffect(() => {
        loadUser();
    }, [loadUser]);

    return (
        <div className="min-h-screen flex flex-col bg-gray-50">
            <Toaster position="top-right" />
            <Header />
            <main className="flex-grow">
                <Routes>
                    <Route path="/" element={<Home />} />
                    <Route path="/login" element={<Login />} />
                    <Route path="/register" element={<Register />} />
                    <Route path="/documents" element={<Documents />} />
                    <Route path="/documents/:slug" element={<DocumentDetail />} />
                    <Route path="/categories" element={<Categories />} />
                    <Route path="/profile" element={<Profile />} />
                    <Route path="/contact" element={<Contact />} />

                    {/* Admin Routes */}
                    <Route path="/admin" element={<AdminLayout />}>
                        <Route index element={<Dashboard />} />
                        <Route path="documents" element={<DocumentList />} />
                        <Route path="documents/create" element={<CreateDocument />} />
                        <Route path="documents/edit/:id" element={<EditDocument />} />

                        <Route path="categories" element={<CategoryList />} />
                        <Route path="categories/create" element={<CreateCategory />} />

                        <Route path="users" element={<UserList />} />
                        <Route path="users/create" element={<CreateUser />} />
                        <Route path="users/edit/:id" element={<EditUser />} />
                        <Route path="categories/edit/:id" element={<CreateCategory />} />
                    </Route>
                </Routes>
            </main>
            <Footer />
        </div>
    );
}

export default App;
