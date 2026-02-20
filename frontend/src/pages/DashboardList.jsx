import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Layout, Spin, message, Button, Row, Col, Card, Typography, Modal, Input, Form } from 'antd';
import { LogoutOutlined, PlusOutlined, EnvironmentOutlined, MessageOutlined, DeleteOutlined, EditOutlined, SettingOutlined } from '@ant-design/icons';
import api from '../api';

const { Header, Content } = Layout;
const { Title, Text } = Typography;

const DashboardList = () => {
    const navigate = useNavigate();
    const [companies, setCompanies] = useState([]);
    const [userEmail, setUserEmail] = useState('');
    const [loading, setLoading] = useState(true);
    
    const [isAddModalVisible, setIsAddModalVisible] = useState(false);
    const [confirmLoading, setConfirmLoading] = useState(false);
    
    const [isEditModalVisible, setIsEditModalVisible] = useState(false);
    const [editingCompany, setEditingCompany] = useState(null);

    const [editForm] = Form.useForm();
    const [form] = Form.useForm();

    const fetchData = async () => {
        try {
            const [userRes, companiesRes] = await Promise.all([
                api.get('/users/me'),
                api.get('/companies/')
            ]);
            setUserEmail(userRes.data.email);
            setCompanies(companiesRes.data);
        } catch (error) {
            message.error('Ошибка загрузки данных');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    const handleLogout = () => {
        localStorage.removeItem('token');
        navigate('/login');
    }

    const handleAddCompany = async () => {
        try {
            const values = await form.validateFields();

            if (!values.url_yandex && !values.url_2gis) {
                message.warning('Укажите хотя бы одну ссылку (Яндекс или 2ГИС)');
                return;
            }

            setConfirmLoading(true);
            
            await api.post('/companies/', { 
                name: values.name, 
                url_yandex: values.url_yandex,
                url_2gis: values.url_2gis
            });
            
            message.success('Компания добавлена');
            setIsAddModalVisible(false);
            form.resetFields();

            const res = await api.get('/companies/');
            setCompanies(res.data);
        } catch (error) {
            console.error(error);
            const msg = error.response?.data?.detail || 'Ошибка при добавлении';
            message.error(Array.isArray(msg) ? msg[0].msg : msg);
        } finally {
            setConfirmLoading(false);
        }
    };

    const handleDeleteCompany = async (id) => {
        Modal.confirm({
            title: 'Вы уверены?',
            content: 'Это действие нельзя отменить. Все собранные отзывы будут удалены.',
            okText: 'Да, удалить',
            okType: 'danger',
            cancelText: 'Отмена',
            onOk: async () => {
                try {
                    await api.delete(`/companies/${id}`);
                    message.success('Удалено');
                    setCompanies(prev => prev.filter(c => c.id !== id));
                } catch (error) {
                    message.error('Ошибка удаления');
                }
            }
        });
    };

    const openEditModal = (company) => {
        setEditingCompany(company);
        editForm.setFieldsValue({
            name: company.name,
            url_yandex: company.url_yandex,
            url_2gis: company.url_2gis
        });
        setIsEditModalVisible(true);
    };

    const handleUpdateCompany = async () => {
        try {
            const values = await editForm.validateFields();
            setConfirmLoading(true);
            
            await api.put(`/companies/${editingCompany.id}`, {
                name: values.name,
                url_yandex: values.url_yandex,
                url_2gis: values.url_2gis
            });
            
            message.success('Обновлено!');
            setIsEditModalVisible(false);
            
            const res = await api.get('/companies/');
            setCompanies(res.data);
        } catch (error) {
            message.error('Ошибка обновления');
        } finally {
            setConfirmLoading(false);
        }
    };

    if (loading) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />;

    return (
        <Layout style={{ minHeight: '100vh' }}>
            <Header style={{ background: '#fff', padding: '0 24px', display: 'flex', alignItems: 'center',
                    justifyContent: 'space-between', boxShadow: '0 2px 8px #f0f1f2', zIndex: 1}}>

                <div style={{ fontSize: 20, fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: 15 }}>
                    <img src="/logo.png" alt="Logo" style={{ width: 32, height: 32 }} />
                    Sentiment Guard
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10}}>
                    <Text strong>{userEmail}</Text>
                    <Button 
                        type="primary" 
                        icon={<LogoutOutlined />} 
                        onClick={handleLogout} 
                    >
                        Выйти
                    </Button>
                </div>
            </Header>

            <Content style={{ padding: '24px' }}>
                <Title level={3} style={{ marginBottom: 24 }}>Мои компании</Title>

                <Row gutter={[24, 24]}>

                    <Col xs={24} sm={12} md={8} lg={6}>
                        <Button 
                            type="dashed" 
                            style={{ width: '100%', height: '180px', fontSize: '16px', color: '#999' }}
                            icon={<PlusOutlined />}
                            onClick={() => setIsAddModalVisible(true)}
                        >
                            Добавить компанию
                        </Button>
                    </Col>

                    {companies.map(item => (
                        <Col key={item.id} xs={24} sm={12} md={8} lg={6}>
                            <Card
                                hoverable 
                                style={{ height: '180px', display: 'flex', flexDirection: 'column' }}
                                styles={{ body: { flex: 1 } }}
                                actions={[
                                    <SettingOutlined key="edit" onClick={(e) => { e.stopPropagation(); openEditModal(item); }} />,
                                    <DeleteOutlined key="delete" style={{ color: 'red' }} onClick={(e) => { e.stopPropagation(); handleDeleteCompany(item.id); }} />
                                ]}
                                onClick={() => navigate(`/company/${item.id}`)}
                            >
                                <Card.Meta
                                    title={item.name}
                                    description={
                                        <div style={{ marginTop: 10 }}>
                                            <div style={{ marginBottom: 5, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                                                <EnvironmentOutlined /> {item.address || "Адрес не указан"}
                                            </div>
                                            <div>
                                                <MessageOutlined /> Отзывов: <b>{item.reviews ? item.reviews.length : 0}</b>
                                            </div>
                                        </div>
                                    }
                                />
                            </Card>
                        </Col>
                    ))}
                </Row>
            </Content>

            <Modal
                title="Добавить новую компанию"
                open={isAddModalVisible}
                onOk={handleAddCompany}
                onCancel={() => setIsAddModalVisible(false)}
                confirmLoading={confirmLoading}
            >
                <Form form={form} layout="vertical">
                    <Form.Item
                        name="name"
                        label="Название компании"
                        rules={[{ required: true, message: 'Введите название' }]}
                    >
                        <Input placeholder="Например: Кофейня Ромашка" />
                    </Form.Item>

                    <Form.Item
                        name="url_yandex"
                        label="Ссылка на отзывы (Яндекс.Карты)"
                        rules={[
                            { type: 'url', message: 'Это должна быть валидная ссылка' }
                        ]}
                    >
                        <Input placeholder="https://yandex.ru/maps/..." />
                    </Form.Item>

                    <Form.Item
                        name="url_2gis"
                        label="Ссылка на отзывы (2GIS)"
                        rules={[
                            { type: 'url', message: 'Это должна быть валидная ссылка' }
                        ]}
                    >
                        <Input placeholder="https://2gis.ru/..." />
                    </Form.Item>

                    <Text type="secondary" style={{ fontSize: 12 }}>
                        * Укажите хотя бы одну ссылку
                    </Text>
                </Form>
            </Modal>

            <Modal
                title="Настройки компании"
                open={isEditModalVisible}
                onOk={handleUpdateCompany}
                onCancel={() => setIsEditModalVisible(false)}
                confirmLoading={confirmLoading}
            >
                <Form form={editForm} layout="vertical">
                    <Form.Item name="name" label="Название" rules={[{ required: true }]}>
                        <Input />
                    </Form.Item>
                    <Form.Item name="url_yandex" label="Ссылка Яндекс">
                        <Input />
                    </Form.Item>
                    <Form.Item name="url_2gis" label="Ссылка 2ГИС">
                        <Input />
                    </Form.Item>
                </Form>
            </Modal>
        </Layout>
    );
}

export default DashboardList;
