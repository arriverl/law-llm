import React, { useState } from 'react';
import {
  Card,
  Row,
  Col,
  Statistic,
  Typography,
  Select,
  DatePicker,
  Space,
  Button,
  Progress,
  List,
  Tag,
  Tooltip,
  message,
} from 'antd';
import {
  UserOutlined,
  MessageOutlined,
  TeamOutlined,
  BookOutlined,
  ArrowUpOutlined,
  ArrowDownOutlined,
  DownloadOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import { useQuery } from 'react-query';
import { analyticsAPI } from '../services/api';
import ReactECharts from 'echarts-for-react';
import moment from 'moment';

const { Title, Text } = Typography;
const { RangePicker } = DatePicker;
const { Option } = Select;

const Analytics: React.FC = () => {
  const [timeRange, setTimeRange] = useState(30);
  const [dateRange, setDateRange] = useState<any>(null);

  // 获取分析概览
  const { data: overviewData, isLoading: overviewLoading } = useQuery(
    'analytics-overview',
    analyticsAPI.getOverview,
    {
      refetchInterval: 30000,
    }
  );

  // 获取咨询分析
  const { data: consultationData } = useQuery(
    ['consultation-analytics', timeRange],
    () => analyticsAPI.getConsultationAnalytics(timeRange)
  );

  // 获取生态分析
  const { data: ecosystemData } = useQuery(
    'ecosystem-analytics',
    analyticsAPI.getEcosystemAnalytics
  );

  // 获取商业指标
  const { data: businessData } = useQuery(
    'business-metrics',
    analyticsAPI.getBusinessMetrics
  );

  // 获取AI性能指标
  const { data: aiPerformanceData } = useQuery(
    'ai-performance',
    analyticsAPI.getAIPerformance
  );

  // 咨询趋势图表
  const consultationTrendOption = {
    title: {
      text: `近${timeRange}天咨询趋势`,
      left: 'center',
      textStyle: { fontSize: 14 }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    xAxis: {
      type: 'category',
      data: consultationData?.data?.daily_consultations?.map((item: any) => item.date) || []
    },
    yAxis: {
      type: 'value',
      name: '咨询数量'
    },
    series: [{
      name: '咨询数量',
      data: consultationData?.data?.daily_consultations?.map((item: any) => item.count) || [],
      type: 'line',
      smooth: true,
      itemStyle: { color: '#1890ff' },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [{
            offset: 0, color: 'rgba(24, 144, 255, 0.3)'
          }, {
            offset: 1, color: 'rgba(24, 144, 255, 0.1)'
          }]
        }
      }
    }]
  };

  // 分类分布图表
  const categoryDistributionOption = {
    title: {
      text: '法律咨询分类分布',
      left: 'center',
      textStyle: { fontSize: 14 }
    },
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    series: [{
      name: '咨询分类',
      type: 'pie',
      radius: ['40%', '70%'],
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

  // 合作伙伴增长图表
  const partnerGrowthOption = {
    title: {
      text: '合作伙伴增长趋势',
      left: 'center',
      textStyle: { fontSize: 14 }
    },
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: ecosystemData?.data?.partner_growth?.map((item: any) => item.month) || []
    },
    yAxis: {
      type: 'value',
      name: '合作伙伴数量'
    },
    series: [{
      name: '合作伙伴数量',
      data: ecosystemData?.data?.partner_growth?.map((item: any) => item.count) || [],
      type: 'bar',
      itemStyle: { color: '#52c41a' }
    }]
  };

  // 服务利用率图表
  const serviceUtilizationOption = {
    title: {
      text: '服务利用率',
      left: 'center',
      textStyle: { fontSize: 14 }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    xAxis: {
      type: 'category',
      data: Object.keys(ecosystemData?.data?.service_utilization || {})
    },
    yAxis: {
      type: 'value',
      name: '利用率(%)'
    },
    series: [{
      name: '利用率',
      data: Object.values(ecosystemData?.data?.service_utilization || {}),
      type: 'bar',
      itemStyle: { color: '#faad14' }
    }]
  };

  const handleExport = () => {
    // 实现数据导出功能
    message.info('数据导出功能开发中...');
  };

  return (
    <div>
      <Title level={2} style={{ marginBottom: '24px' }}>
        数据分析
      </Title>

      {/* 时间范围选择 */}
      <Card style={{ marginBottom: '24px' }}>
        <Row justify="space-between" align="middle">
          <Col>
            <Space>
              <Text strong>时间范围：</Text>
              <Select
                value={timeRange}
                onChange={setTimeRange}
                style={{ width: 120 }}
              >
                <Option value={7}>近7天</Option>
                <Option value={30}>近30天</Option>
                <Option value={90}>近90天</Option>
                <Option value={365}>近1年</Option>
              </Select>
              <RangePicker
                value={dateRange}
                onChange={setDateRange}
                placeholder={['开始日期', '结束日期']}
              />
            </Space>
          </Col>
          <Col>
            <Space>
              <Button icon={<ReloadOutlined />} onClick={() => window.location.reload()}>
                刷新
              </Button>
              <Button icon={<DownloadOutlined />} onClick={handleExport}>
                导出数据
              </Button>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* 核心指标 */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="总用户数"
              value={overviewData?.data?.total_users || 0}
              prefix={<UserOutlined />}
              valueStyle={{ color: '#1890ff' }}
              suffix={
                <Tooltip title="较上月增长">
                  <ArrowUpOutlined style={{ color: '#52c41a' }} />
                </Tooltip>
              }
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
              <Title level={4}>平均响应时间</Title>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#faad14' }}>
                {consultationData?.data?.response_time_avg || 0}s
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

      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} lg={12}>
          <Card>
            <ReactECharts
              option={partnerGrowthOption}
              style={{ height: '300px' }}
            />
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card>
            <ReactECharts
              option={serviceUtilizationOption}
              style={{ height: '300px' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 商业指标 */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} lg={8}>
          <Card title="收入指标">
            <List
              dataSource={[
                { label: '月收入', value: `¥${(businessData?.data?.revenue_metrics?.monthly_revenue || 0).toLocaleString()}` },
                { label: '收入增长率', value: `${businessData?.data?.revenue_metrics?.revenue_growth_rate || 0}%` },
                { label: '人均收入', value: `¥${(businessData?.data?.revenue_metrics?.average_revenue_per_user || 0).toLocaleString()}` },
              ]}
              renderItem={(item) => (
                <List.Item>
                  <List.Item.Meta
                    title={item.label}
                    description={<Text strong>{item.value}</Text>}
                  />
                </List.Item>
              )}
            />
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card title="成本降低">
            <List
              dataSource={[
                { label: '法律服务成本降低', value: `${businessData?.data?.cost_reduction?.legal_service_cost_reduction || 0}%` },
                { label: '文档处理时间减少', value: `${businessData?.data?.cost_reduction?.document_processing_time_reduction || 0}%` },
                { label: '人工工作减少', value: `${businessData?.data?.cost_reduction?.manual_work_reduction || 0}%` },
                { label: '总成本节约', value: `¥${(businessData?.data?.cost_reduction?.total_cost_savings || 0).toLocaleString()}` },
              ]}
              renderItem={(item) => (
                <List.Item>
                  <List.Item.Meta
                    title={item.label}
                    description={<Text strong>{item.value}</Text>}
                  />
                </List.Item>
              )}
            />
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card title="AI性能指标">
            <List
              dataSource={[
                { label: 'DeepSeek R1准确率', value: `${aiPerformanceData?.data?.model_accuracy?.deepseek_r1 || 0}%` },
                { label: 'BERT法律准确率', value: `${aiPerformanceData?.data?.model_accuracy?.bert_legal || 0}%` },
                { label: '法律分类器准确率', value: `${aiPerformanceData?.data?.model_accuracy?.legal_classifier || 0}%` },
                { label: '平均置信度', value: `${Math.round((aiPerformanceData?.data?.response_quality?.average_confidence || 0) * 100)}%` },
                { label: '平均响应时间', value: `${aiPerformanceData?.data?.processing_metrics?.average_response_time || 0}s` },
              ]}
              renderItem={(item) => (
                <List.Item>
                  <List.Item.Meta
                    title={item.label}
                    description={<Text strong>{item.value}</Text>}
                  />
                </List.Item>
              )}
            />
          </Card>
        </Col>
      </Row>

      {/* 市场渗透率 */}
      <Card title="市场渗透率">
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12} lg={6}>
            <div style={{ textAlign: 'center' }}>
              <Title level={3} style={{ color: '#1890ff' }}>
                {businessData?.data?.market_penetration?.gba_penetration_rate || 0}%
              </Title>
              <Text>粤港澳大湾区渗透率</Text>
            </div>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <div style={{ textAlign: 'center' }}>
              <Title level={3} style={{ color: '#52c41a' }}>
                {businessData?.data?.market_penetration?.enterprise_adoption_rate || 0}%
              </Title>
              <Text>企业采用率</Text>
            </div>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <div style={{ textAlign: 'center' }}>
              <Title level={3} style={{ color: '#faad14' }}>
                {businessData?.data?.market_penetration?.government_adoption_rate || 0}%
              </Title>
              <Text>政府采用率</Text>
            </div>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <div style={{ textAlign: 'center' }}>
              <Title level={3} style={{ color: '#722ed1' }}>
                {businessData?.data?.market_penetration?.law_firm_adoption_rate || 0}%
              </Title>
              <Text>律所采用率</Text>
            </div>
          </Col>
        </Row>
      </Card>
    </div>
  );
};

export default Analytics;
