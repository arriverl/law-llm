import React, { useEffect, useState } from 'react';
import { Row, Col, Card, Statistic, Typography, Space, Progress, List, Avatar, Tag } from 'antd';
import {
  UserOutlined,
  MessageOutlined,
  BookOutlined,
  TeamOutlined,
  ArrowUpOutlined,
  ArrowDownOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
} from '@ant-design/icons';
import { useQuery } from 'react-query';
import { analyticsAPI, legalAIAPI } from '../services/api';
import ReactECharts from 'echarts-for-react';

const { Title, Text } = Typography;

const Dashboard: React.FC = () => {
  const [recentConsultations, setRecentConsultations] = useState([]);

  // 获取分析概览数据
  const { data: overviewData, isLoading: overviewLoading } = useQuery(
    'analytics-overview',
    analyticsAPI.getOverview,
    {
      refetchInterval: 30000, // 30秒刷新一次
    }
  );

  // 获取咨询分析数据
  const { data: consultationData } = useQuery(
    'consultation-analytics',
    () => analyticsAPI.getConsultationAnalytics(7),
    {
      refetchInterval: 60000, // 1分钟刷新一次
    }
  );

  // 获取AI模型状态
  const { data: modelStatus } = useQuery(
    'model-status',
    legalAIAPI.getModelStatus,
    {
      refetchInterval: 30000,
    }
  );

  // 获取最近咨询记录
  useEffect(() => {
    const fetchRecentConsultations = async () => {
      try {
        const response = await legalAIAPI.getConsultations(0, 5);
        setRecentConsultations(response.data.consultations || []);
      } catch (error) {
        console.error('获取最近咨询失败:', error);
      }
    };

    fetchRecentConsultations();
  }, []);

  // 咨询趋势图表配置
  const consultationTrendOption = {
    title: {
      text: '近7天咨询趋势',
      left: 'center',
      textStyle: { fontSize: 14 }
    },
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: consultationData?.data?.daily_consultations?.map((item: any) => item.date) || []
    },
    yAxis: {
      type: 'value'
    },
    series: [{
      data: consultationData?.data?.daily_consultations?.map((item: any) => item.count) || [],
      type: 'line',
      smooth: true,
      itemStyle: { color: '#1890ff' }
    }]
  };

  // 分类分布图表配置
  const categoryDistributionOption = {
    title: {
      text: '法律咨询分类分布',
      left: 'center',
      textStyle: { fontSize: 14 }
    },
    tooltip: {
      trigger: 'item'
    },
    series: [{
      type: 'pie',
      radius: '60%',
      data: Object.entries(consultationData?.data?.category_distribution || {}).map(([name, value]) => ({
        name,
        value
      })),
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }]
  };

  return (
    <div>
      <Title level={2} style={{ marginBottom: '24px' }}>
        系统概览
      </Title>

      {/* 核心指标卡片 */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="总用户数"
              value={overviewData?.data?.total_users || 0}
              prefix={<UserOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="总咨询数"
              value={overviewData?.data?.total_consultations || 0}
              prefix={<MessageOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="生态合作伙伴"
              value={overviewData?.data?.total_partners || 0}
              prefix={<TeamOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="知识库条目"
              value={overviewData?.data?.total_knowledge || 0}
              prefix={<BookOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 性能指标 */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={12} lg={8}>
          <Card>
            <div style={{ textAlign: 'center' }}>
              <Title level={4}>咨询成功率</Title>
              <Progress
                type="circle"
                percent={Math.round(overviewData?.data?.consultation_success_rate || 0)}
                strokeColor="#52c41a"
                size={120}
              />
            </div>
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={8}>
          <Card>
            <div style={{ textAlign: 'center' }}>
              <Title level={4}>用户满意度</Title>
              <Progress
                type="circle"
                percent={Math.round((overviewData?.data?.user_satisfaction_score || 0) * 20)}
                strokeColor="#1890ff"
                size={120}
              />
            </div>
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={8}>
          <Card>
            <div style={{ textAlign: 'center' }}>
              <Title level={4}>AI模型状态</Title>
              <div style={{ marginTop: '16px' }}>
                {modelStatus?.data?.status === 'active' ? (
                  <Tag color="green" icon={<CheckCircleOutlined />}>
                    运行正常
                  </Tag>
                ) : (
                  <Tag color="red" icon={<ClockCircleOutlined />}>
                    服务异常
                  </Tag>
                )}
              </div>
            </div>
          </Card>
        </Col>
      </Row>

      {/* 图表区域 */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} lg={12}>
          <Card>
            <ReactECharts
              option={consultationTrendOption}
              style={{ height: '300px' }}
            />
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card>
            <ReactECharts
              option={categoryDistributionOption}
              style={{ height: '300px' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 最近咨询记录 */}
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <Card title="最近咨询记录" size="small">
            <List
              dataSource={recentConsultations}
              renderItem={(item: any) => (
                <List.Item>
                  <List.Item.Meta
                    avatar={<Avatar icon={<MessageOutlined />} />}
                    title={
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Text ellipsis style={{ maxWidth: '200px' }}>
                          {item.question}
                        </Text>
                        <Tag color={item.status === 'completed' ? 'green' : 'orange'}>
                          {item.status === 'completed' ? '已完成' : '处理中'}
                        </Tag>
                      </div>
                    }
                    description={
                      <Space direction="vertical" size="small">
                        <Text type="secondary" style={{ fontSize: '12px' }}>
                          分类: {item.category || '未分类'}
                        </Text>
                        <Text type="secondary" style={{ fontSize: '12px' }}>
                          置信度: {Math.round((parseFloat(item.confidence) || 0) * 100)}%
                        </Text>
                        <Text type="secondary" style={{ fontSize: '12px' }}>
                          {new Date(item.created_at).toLocaleString()}
                        </Text>
                      </Space>
                    }
                  />
                </List.Item>
              )}
            />
          </Card>
        </Col>
        
        <Col xs={24} lg={12}>
          <Card title="系统状态" size="small">
            <List
              dataSource={[
                { name: 'DeepSeek R1模型', status: modelStatus?.data?.models?.deepseek_r1 === 'available' ? '正常' : '异常', color: modelStatus?.data?.models?.deepseek_r1 === 'available' ? 'green' : 'red' },
                { name: 'BERT模型', status: modelStatus?.data?.models?.bert === 'available' ? '正常' : '异常', color: modelStatus?.data?.models?.bert === 'available' ? 'green' : 'red' },
                { name: '法律分类器', status: modelStatus?.data?.models?.legal_classifier === 'available' ? '正常' : '异常', color: modelStatus?.data?.models?.legal_classifier === 'available' ? 'green' : 'red' },
                { name: '知识库服务', status: '正常', color: 'green' },
                { name: '生态协同服务', status: '正常', color: 'green' },
              ]}
              renderItem={(item) => (
                <List.Item>
                  <List.Item.Meta
                    title={item.name}
                    description={
                      <Tag color={item.color}>
                        {item.status}
                      </Tag>
                    }
                  />
                </List.Item>
              )}
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;
