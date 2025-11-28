import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Layout, Spin, message, Button, Row, Col, Card, Statistic } from 'antd';
import { ReloadOutlined, ArrowLeftOutlined, StarFilled } from '@ant-design/icons';
import api from '../api';

const { Header, Content } = Layout;

const CompanyDashboard = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const [company, setCompany] = useState(null);
  const [loading, setLoading] = useState(true);

  const [parsing, setParsing] = useState(false);
    
  const fetchCompany = async () => {
    try {
      const res = await api.get(`/companies/${id}`);
      console.log("Данные пришли:", res.data);
      setCompany(res.data);
    } catch (error) {
      message.error('Не удалось загрузить компанию');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCompany();
  }, [id]);

  const handleParse = async () => {
    setParsing(true);
    message.loading({ content: 'Парсинг запущен... (это займет 15-40 секунд)', key: 'parseMsg' });

    try {
        const response = await api.post(`/companies/${id}/fetch-reviews/`);

        message.success({ content: res.data.message, key: 'parseMsg', duration: 3 });

        fetchCompany();
    } catch (error) {
        const errorMsg = error.response?.data?.detail || 'Ошибка при запуске парсинга';
        message.error({ content: errorMsg, key: 'parseMsg', duration: 5 });
    } finally {
        setParsing(false);
    }
  };

  if (loading) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />;
  if (!company) return <div>Компания не найдена</div>;

  const totalReviews = company.reviews.length;

  const avgRating = totalReviews > 0
    ? (company.reviews.reduce((sum, r) => sum + r.rating, 0) / totalReviews).toFixed(2)
    : 'N/A';

  const positiveCount = company.reviews.filter(r => r.sentiment === 'positive').length;

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ background: '#fff', padding: '0 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', boxShadow: '0 2px 8px #f0f1f2' }}>
        <div style={{ fontSize: 20, fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: 15 }}>
            <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/')} />
            {company.name}
        </div>
        
        <Button 
            type="primary" 
            icon={<ReloadOutlined />} 
            onClick={handleParse} 
            loading={parsing}
        >
            Обновить отзывы
        </Button>
      </Header>
      
      <Content style={{ padding: '24px' }}>
        
        <Row gutter={16} style={{ marginBottom: 24 }}>
          <Col span={8}>
            <Card hoverable>
              <Statistic title="Всего отзывов" value={totalReviews} />
            </Card>
          </Col>
          <Col span={8}>
            <Card hoverable>
              <Statistic 
                title="Средний рейтинг" 
                value={avgRating} 
                precision={1} 
                valueStyle={{ color: '#faad14' }}
                prefix={<StarFilled />}
              />
            </Card>
          </Col>
          <Col span={8}>
            <Card hoverable>
              <Statistic 
                title="Позитивных отзывов" 
                value={positiveCount} 
                valueStyle={{ color: '#3f8600' }} 
                suffix={`/ ${totalReviews}`}
              />
            </Card>
          </Col>
        </Row>

        <Card style={{ textAlign: 'center', color: '#999' }}>
            Здесь будут графики и список отзывов...
        </Card>

      </Content>
    </Layout>
  );
};

export default CompanyDashboard;
