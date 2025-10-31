import React, { useState } from 'react';
import {
  Card,
  Table,
  Button,
  Space,
  Tag,
  Typography,
  Modal,
  Form,
  Input,
  Select,
  message,
  Row,
  Col,
  Statistic,
  Progress,
  Avatar,
  Tooltip,
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  TeamOutlined,
  GlobalOutlined,
  BankOutlined,
  ShopOutlined,
  FileTextOutlined,
  ShareAltOutlined,
} from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { ecosystemAPI } from '../services/api';

const { Title, Text } = Typography;
const { Option } = Select;

interface Partner {
  id: number;
  name: string;
  type: string;
  region: string;
  contact_info: Record<string, any>;
  services: string[];
  status: string;
  created_at: string;
}

const Ecosystem: React.FC = () => {
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editingPartner, setEditingPartner] = useState<Partner | null>(null);
  const [form] = Form.useForm();
  const queryClient = useQueryClient();

  // 获取合作伙伴列表
  const { data: partnersData, isLoading } = useQuery(
    'ecosystem-partners',
    () => ecosystemAPI.getPartners(undefined, undefined, 0, 100)
  );

  // 获取生态统计
  const { data: statsData } = useQuery('ecosystem-stats', ecosystemAPI.getStats);

  // 获取支持地区
  const { data: regionsData } = useQuery('ecosystem-regions', ecosystemAPI.getRegions);

  // 创建合作伙伴
  const createMutation = useMutation(ecosystemAPI.createPartner, {
    onSuccess: () => {
      message.success('合作伙伴创建成功');
      setIsModalVisible(false);
      form.resetFields();
      queryClient.invalidateQueries('ecosystem-partners');
      queryClient.invalidateQueries('ecosystem-stats');
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || '创建失败');
    },
  });

  // 更新合作伙伴
  const updateMutation = useMutation(
    ({ id, data }: { id: number; data: any }) => ecosystemAPI.updatePartner(id, data),
    {
      onSuccess: () => {
        message.success('合作伙伴更新成功');
        setIsModalVisible(false);
        setEditingPartner(null);
        form.resetFields();
        queryClient.invalidateQueries('ecosystem-partners');
      },
      onError: (error: any) => {
        message.error(error.response?.data?.detail || '更新失败');
      },
    }
  );

  // 删除合作伙伴
  const deleteMutation = useMutation(ecosystemAPI.deletePartner, {
    onSuccess: () => {
      message.success('合作伙伴删除成功');
      queryClient.invalidateQueries('ecosystem-partners');
      queryClient.invalidateQueries('ecosystem-stats');
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || '删除失败');
    },
  });

  // 部署智能合约
  const contractMutation = useMutation(ecosystemAPI.deploySmartContract, {
    onSuccess: () => {
      message.success('智能合约部署已启动');
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || '部署失败');
    },
  });

  // 启动数据共享
  const sharingMutation = useMutation(ecosystemAPI.initiateDataSharing, {
    onSuccess: () => {
      message.success('数据共享已启动');
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || '启动失败');
    },
  });

  const handleCreate = () => {
    setEditingPartner(null);
    form.resetFields();
    setIsModalVisible(true);
  };

  const handleEdit = (partner: Partner) => {
    setEditingPartner(partner);
    form.setFieldsValue({
      name: partner.name,
      type: partner.type,
      region: partner.region,
      contact_info: partner.contact_info,
      services: partner.services,
    });
    setIsModalVisible(true);
  };

  const handleDelete = (id: number) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除这个合作伙伴吗？',
      onOk: () => deleteMutation.mutate(id),
    });
  };

  const handleSubmit = (values: any) => {
    if (editingPartner) {
      updateMutation.mutate({ id: editingPartner.id, data: values });
    } else {
      createMutation.mutate(values);
    }
  };

  const handleDeployContract = () => {
    Modal.confirm({
      title: '部署智能合约',
      content: '确定要部署智能合约吗？这将启动区块链部署流程。',
      onOk: () => {
        contractMutation.mutate({
          contract_type: 'legal_service',
          parties: ['system', 'partners'],
          terms: { version: '1.0', jurisdiction: 'GBA' },
          jurisdiction: 'GBA',
        });
      },
    });
  };

  const handleDataSharing = (partnerId: number) => {
    sharingMutation.mutate({
      partner_id: partnerId,
      data_type: 'legal_knowledge',
      sharing_level: 'restricted',
      purpose: 'collaboration',
    });
  };

  const getPartnerIcon = (type: string) => {
    switch (type) {
      case 'government':
        return <BankOutlined />;
      case 'enterprise':
        return <ShopOutlined />;
      case 'law_firm':
        return <FileTextOutlined />;
      default:
        return <TeamOutlined />;
    }
  };

  const getPartnerTypeName = (type: string) => {
    switch (type) {
      case 'government':
        return '政府机构';
      case 'enterprise':
        return '企业';
      case 'law_firm':
        return '律师事务所';
      default:
        return '其他';
    }
  };

  const columns = [
    {
      title: '合作伙伴',
      dataIndex: 'name',
      key: 'name',
      render: (text: string, record: Partner) => (
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <Avatar
            icon={getPartnerIcon(record.type)}
            style={{ marginRight: '8px', backgroundColor: '#1890ff' }}
          />
          <div>
            <Text strong>{text}</Text>
            <br />
            <Text type="secondary" style={{ fontSize: '12px' }}>
              {getPartnerTypeName(record.type)}
            </Text>
          </div>
        </div>
      ),
    },
    {
      title: '地区',
      dataIndex: 'region',
      key: 'region',
      render: (region: string) => (
        <Tag icon={<GlobalOutlined />} color="blue">
          {region}
        </Tag>
      ),
    },
    {
      title: '服务',
      dataIndex: 'services',
      key: 'services',
      render: (services: string[]) => (
        <Space wrap>
          {services.map((service) => (
            <Tag key={service}>
              {service}
            </Tag>
          ))}
        </Space>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={status === 'active' ? 'green' : 'red'}>
          {status === 'active' ? '活跃' : '非活跃'}
        </Tag>
      ),
    },
    {
      title: '操作',
      key: 'actions',
      render: (_: any, record: Partner) => (
        <Space>
          <Button
            type="text"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Button
            type="text"
            icon={<ShareAltOutlined />}
            onClick={() => handleDataSharing(record.id)}
          >
            数据共享
          </Button>
          <Button
            type="text"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDelete(record.id)}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Title level={2} style={{ marginBottom: '24px' }}>
        生态协同管理
      </Title>

      {/* 统计概览 */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="总合作伙伴"
              value={statsData?.data?.total_partners || 0}
              prefix={<TeamOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="政府机构"
              value={statsData?.data?.government_partners || 0}
              prefix={<BankOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="企业伙伴"
              value={statsData?.data?.enterprise_partners || 0}
              prefix={<ShopOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="律师事务所"
              value={statsData?.data?.law_firm_partners || 0}
              prefix={<FileTextOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 操作区域 */}
      <Card style={{ marginBottom: '24px' }}>
        <Row justify="space-between" align="middle">
          <Col>
            <Title level={4} style={{ margin: 0 }}>
              合作伙伴管理
            </Title>
          </Col>
          <Col>
            <Space>
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={handleCreate}
              >
                添加合作伙伴
              </Button>
              <Button
                icon={<FileTextOutlined />}
                onClick={handleDeployContract}
              >
                部署智能合约
              </Button>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* 合作伙伴列表 */}
      <Card>
        <Table
          columns={columns}
          dataSource={partnersData?.data || []}
          loading={isLoading}
          rowKey="id"
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条记录`,
          }}
        />
      </Card>

      {/* 创建/编辑模态框 */}
      <Modal
        title={editingPartner ? '编辑合作伙伴' : '添加合作伙伴'}
        open={isModalVisible}
        onCancel={() => {
          setIsModalVisible(false);
          setEditingPartner(null);
          form.resetFields();
        }}
        footer={null}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Form.Item
            name="name"
            label="合作伙伴名称"
            rules={[{ required: true, message: '请输入合作伙伴名称' }]}
          >
            <Input placeholder="请输入合作伙伴名称" />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="type"
                label="类型"
                rules={[{ required: true, message: '请选择类型' }]}
              >
                <Select placeholder="请选择类型">
                  <Option value="government">政府机构</Option>
                  <Option value="enterprise">企业</Option>
                  <Option value="law_firm">律师事务所</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="region"
                label="地区"
                rules={[{ required: true, message: '请选择地区' }]}
              >
                <Select placeholder="请选择地区">
                  {regionsData?.data?.regions?.map((region: any) => (
                    <Option key={region.code} value={region.code}>
                      {region.name}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            name="services"
            label="提供服务"
            rules={[{ required: true, message: '请选择提供的服务' }]}
          >
            <Select
              mode="multiple"
              placeholder="请选择提供的服务"
            >
              <Option value="legal_consultation">法律咨询</Option>
              <Option value="document_analysis">文档分析</Option>
              <Option value="case_research">案例研究</Option>
              <Option value="contract_review">合同审查</Option>
              <Option value="data_sharing">数据共享</Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="contact_info"
            label="联系信息"
            rules={[{ required: true, message: '请输入联系信息' }]}
          >
            <Input.TextArea
              rows={3}
              placeholder="请输入联系信息（JSON格式）"
            />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button
                type="primary"
                htmlType="submit"
                loading={createMutation.isLoading || updateMutation.isLoading}
              >
                {editingPartner ? '更新' : '创建'}
              </Button>
              <Button onClick={() => setIsModalVisible(false)}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Ecosystem;
