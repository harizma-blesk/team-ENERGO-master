import { useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import {
  Alert,
  Badge,
  Button,
  Card,
  Col,
  DatePicker,
  Descriptions,
  Empty,
  Form,
  InputNumber,
  List,
  Row,
  Select,
  Space,
  Spin,
  Switch,
  Tag,
  TimePicker,
  Typography
} from 'antd';
import {
  CheckCircleOutlined,
  EnvironmentOutlined,
  ReloadOutlined,
  SearchOutlined,
  VideoCameraOutlined
} from '@ant-design/icons';
import dayjs from 'dayjs';
import { findFreeRooms, loadAuditories, loadLocations } from '../api/rooms-api';

const cameraStatusTag = (room) => {
  if (room.camera_status === 'online' && room.camera_free) {
    return <Tag icon={<VideoCameraOutlined />} color="success">Камера: свободно</Tag>;
  }
  if (room.camera_status === 'online' && !room.camera_free) {
    return <Tag icon={<VideoCameraOutlined />} color="error">Камера: занято</Tag>;
  }
  return <Tag icon={<VideoCameraOutlined />} color="default">Камера: недоступна</Tag>;
};

const CORPUS_TO_ID = { 'А': 'corp_a', 'Б': 'corp_b', 'Д': 'corp_d' };

const RoomsPage = () => {
  const [form] = Form.useForm();
  const [selectedLocation, setSelectedLocation] = useState(null);

  const locationsQuery = useQuery({
    queryKey: ['locations'],
    queryFn: loadLocations,
    retry: 1,
  });

  const auditoriesQuery = useQuery({
    queryKey: ['auditories'],
    queryFn: loadAuditories,
    retry: 1,
  });

  const searchMutation = useMutation({
    mutationFn: findFreeRooms,
  });

  // {"А": [1,2,3], "Б": [1,2,3], "Д": [1,2,3]} → [{id, name, floors}]
  const locationsList = locationsQuery.data
    ? Object.entries(locationsQuery.data).map(([corpus, floors]) => ({
        id: CORPUS_TO_ID[corpus] ?? corpus,
        name: `Корпус ${corpus}`,
        floors,
      }))
    : [];

  const floors = locationsList.find((l) => l.id === selectedLocation)?.floors ?? [];

  const handleSearch = async () => {
    try {
      const values = await form.validateFields();
      const query = {
        location_id: values.location_id,
        start_at: dayjs(values.date)
          .hour(dayjs(values.time).hour())
          .minute(dayjs(values.time).minute())
          .second(0)
          .format('YYYY-MM-DDTHH:mm:ss'),
        duration_minutes: 80,
        floor: values.floor,
        filters: {
          min_capacity: values.min_capacity || undefined,
          need_projector: values.need_projector || undefined,
        },
      };
      searchMutation.mutate(query);
    } catch {
      /* validation errors shown by antd */
    }
  };

  const result = searchMutation.data;

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      {/* Header */}
      <Card>
        <Typography.Title level={3}>
          <EnvironmentOutlined /> Поиск свободных кабинетов
        </Typography.Title>
        <Typography.Text type="secondary">
          Данные по камерам обновляются в реальном времени через YOLO-детекцию. Если камера недоступна — показывается только статус по расписанию.
        </Typography.Text>
      </Card>

      {/* Search form */}
      <Card title="Параметры поиска">
        {locationsQuery.isLoading && <Spin />}
        {locationsQuery.error && (
          <Alert type="warning" showIcon message="Не удалось загрузить список корпусов" />
        )}
        <Form
          form={form}
          layout="vertical"
          initialValues={{
            date: dayjs(),
            time: dayjs().startOf('hour').add(1, 'hour'),
            need_projector: false,
          }}
        >
          <Row gutter={16}>
            <Col xs={24} sm={12} md={6}>
              <Form.Item label="Корпус" name="location_id" rules={[{ required: true }]}>
                <Select
                  placeholder="Выберите корпус"
                  loading={locationsQuery.isLoading}
                  onChange={(v) => {
                    setSelectedLocation(v);
                    form.setFieldValue('floor', undefined);
                  }}
                >
                  {locationsList.map((l) => (
                    <Select.Option key={l.id} value={l.id}>
                      {l.name}
                    </Select.Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>

            <Col xs={24} sm={12} md={4}>
              <Form.Item label="Этаж" name="floor">
                <Select allowClear placeholder="Все">
                  {floors.map((f) => (
                    <Select.Option key={f} value={f}>
                      {f} этаж
                    </Select.Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>

            <Col xs={24} sm={12} md={5}>
              <Form.Item label="Дата" name="date" rules={[{ required: true }]}>
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>

            <Col xs={24} sm={12} md={4}>
              <Form.Item label="Время" name="time" rules={[{ required: true }]}>
                <TimePicker format="HH:mm" minuteStep={15} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col xs={12} sm={6}>
              <Form.Item label="Мин. вместимость" name="min_capacity">
                <InputNumber min={1} max={500} style={{ width: '100%' }} placeholder="—" />
              </Form.Item>
            </Col>

            <Col xs={12} sm={6}>
              <Form.Item label="Нужен проектор" name="need_projector" valuePropName="checked">
                <Switch />
              </Form.Item>
            </Col>

            <Col xs={24} sm={12} style={{ display: 'flex', alignItems: 'flex-end', paddingBottom: 24 }}>
              <Button
                type="primary"
                icon={<SearchOutlined />}
                loading={searchMutation.isPending}
                onClick={handleSearch}
                size="large"
              >
                Найти кабинеты
              </Button>
            </Col>
          </Row>
        </Form>
      </Card>

      {/* Error */}
      {searchMutation.isError && (
        <Alert
          type="error"
          showIcon
          message="Ошибка поиска"
          description={searchMutation.error.message}
          action={
            <Button icon={<ReloadOutlined />} onClick={handleSearch}>
              Повторить
            </Button>
          }
        />
      )}

      {/* Results */}
      {result && (
        <>
          {result.reason && <Alert type="info" showIcon message={result.reason} />}

          <Card
            title={
              <Space>
                <CheckCircleOutlined style={{ color: '#52c41a' }} />
                Свободные кабинеты
                <Badge count={result.free_rooms.length} style={{ backgroundColor: '#52c41a' }} />
              </Space>
            }
          >
            {result.free_rooms.length === 0 ? (
              <Empty description="Свободных кабинетов не найдено" />
            ) : (
              <List
                grid={{ gutter: 16, xs: 1, sm: 2, md: 3, lg: 4 }}
                dataSource={result.free_rooms}
                renderItem={(room) => (
                  <List.Item>
                    <Card size="small" hoverable>
                      <Descriptions column={1} size="small">
                        <Descriptions.Item label="Кабинет">
                          <Typography.Text strong>{room.name}</Typography.Text>
                        </Descriptions.Item>
                        {room.floor != null && (
                          <Descriptions.Item label="Этаж">{room.floor}</Descriptions.Item>
                        )}
                        {room.capacity != null && (
                          <Descriptions.Item label="Вместимость">{room.capacity} чел.</Descriptions.Item>
                        )}
                        <Descriptions.Item label="Расписание">
                          {room.schedule_free ? (
                            <Tag color="success">Свободно</Tag>
                          ) : (
                            <Tag color="error">Занято</Tag>
                          )}
                        </Descriptions.Item>
                        <Descriptions.Item label="Камера">{cameraStatusTag(room)}</Descriptions.Item>
                      </Descriptions>
                    </Card>
                  </List.Item>
                )}
              />
            )}
          </Card>
        </>
      )}

      {/* All auditories list */}
      <Card
        title="Все аудитории"
        extra={
          <Button
            icon={<ReloadOutlined />}
            onClick={() => auditoriesQuery.refetch()}
            loading={auditoriesQuery.isLoading}
          >
            Обновить
          </Button>
        }
      >
        {auditoriesQuery.isLoading && <Spin />}
        {auditoriesQuery.error && (
          <Alert type="warning" showIcon message="Не удалось загрузить список аудиторий (PHP сервер недоступен)" />
        )}
        {auditoriesQuery.data && auditoriesQuery.data.length > 0 ? (
          <List
            size="small"
            dataSource={auditoriesQuery.data}
            renderItem={(aud) => (
              <List.Item>
                <List.Item.Meta
                  title={aud.name || aud.number}
                  description={
                    <Space>
                      <Tag>{aud.corpus}</Tag>
                      <Tag>{aud.category}</Tag>
                    </Space>
                  }
                />
              </List.Item>
            )}
          />
        ) : (
          !auditoriesQuery.isLoading && !auditoriesQuery.error && <Empty description="Нет данных" />
        )}
      </Card>
    </Space>
  );
};

export default RoomsPage;
