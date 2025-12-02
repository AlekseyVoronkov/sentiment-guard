import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Layout, Spin, message, Button, Row, Col, Card, Statistic, List, Tag, Rate } from 'antd';
import { ReloadOutlined, ArrowLeftOutlined, StarFilled } from '@ant-design/icons';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import api from '../api';

const { Header, Content } = Layout;

const SENTIMENT_COLORS = {
  'positive': '#52c41a',
  'neutral': '#faad14',
  'negative': '#f5222d'
};

const CompanyDashboard = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const [company, setCompany] = useState(null);
  const [loading, setLoading] = useState(true);
  const [parsing, setParsing] = useState(false);
    
  const fetchCompany = async () => {
    try {
      const res = await api.get(`/companies/${id}`);
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
        const response = await api.post(`/companies/${id}/fetch-reviews/`, null, {
          timeout: 120000
        });
        message.success({ content: response.data.message, key: 'parseMsg', duration: 3 });
        await fetchCompany();
    } catch (error) {
        console.error(error); 
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
    ? (company.reviews.reduce((sum, r) => sum + r.rating, 0) / totalReviews).toFixed(1)
    : 0;

  const positiveCount = company.reviews.filter(r => r.sentiment === 'positive').length;

  const sentimentStats = company.reviews.reduce((acc, review) => {
    const s = review.sentiment || 'Unknown';
    acc[s] = (acc[s] || 0) + 1;
    return acc;
  }, {});

  const chartData = Object.keys(sentimentStats).map(key => ({
    name: key,
    value: sentimentStats[key]
  }));

  return (
    <Layout style={{ minHeight: '100vh', background: '#f0f2f5' }}>
      <Header style={{ background: '#fff', padding: '0 24px', display: 'flex', alignItems: 'center',
                    justifyContent: 'space-between', boxShadow: '0 2px 8px #f0f1f2', zIndex: 1}}>
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
            <Card hoverable bordered={false}>
              <Statistic title="Всего отзывов" value={totalReviews} />
            </Card>
          </Col>
          <Col span={8}>
            <Card hoverable bordered={false}>
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

        <Row gutter={24}>
          <Col span={8}>
            <Card title="Анализ тональности" bordered={false} style={{ height: '100%' }}>
              {chartData.length > 0 ? (
                <div style={{ width: '100%', height: 300 }}>
                  <ResponsiveContainer>
                    <PieChart>
                      <Pie
                        data={chartData}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={80}
                        paddingAngle={5}
                        dataKey="value"
                      >
                        {chartData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={SENTIMENT_COLORS[entry.name] || '#888'} />
                        ))}
                      </Pie>
                      <Tooltip />
                      <Legend verticalAlign="bottom" height={36}/>
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <div style={{ textAlign: 'center', color: '#999', marginTop: 50 }}>Нет данных</div>
              )}
            </Card>
          </Col>

          <Col span={16}>
            <Card title="Лента отзывов" bordered={false}>
              <List
                itemLayout="vertical"
                size="large"
                pagination={{
                  onChange: (page) => { console.log(page); },
                  pageSize: 5,
                }}
                dataSource={company.reviews}
                renderItem={(item) => (
                  <List.Item
                    key={item.id}
                    actions={[
                        <Rate disabled defaultValue={item.rating} style={{ fontSize: 14 }} />,
                        <span style={{ color: '#888' }}>
                            {new Date(item.date).toLocaleDateString('ru-RU')}
                        </span>
                    ]}
                    extra={
                        <Tag color={SENTIMENT_COLORS[item.sentiment]}>
                            {item.sentiment}
                        </Tag>
                    }
                  >
                    <List.Item.Meta
                      title={<span style={{ fontWeight: 'bold' }}>{item.author}</span>}
                    />
                    {item.text}
                  </List.Item>
                )}
              />
            </Card>
          </Col>
        </Row>

      </Content>
    </Layout>
  );
};

export default CompanyDashboard;
