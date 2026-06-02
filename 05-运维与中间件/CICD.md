# 企业级全栈分布式架构与 CI/CD 自动化流水线搭建指南

> **技术栈**: Python 3.11 + Django 4.2 + MySQL 8.0 (分库分表) + Redis 7.0 (集群) + Nginx + Docker + Kubernetes + Jenkins

---

## 目录

1. [架构总览](#1-架构总览)
2. [环境准备](#2-环境准备)
3. [Django 后端应用开发](#3-django-后端应用开发)
4. [MySQL 分库分表方案](#4-mysql-分库分表方案)
5. [Redis 集群部署](#5-redis-集群部署)
6. [Nginx 反向代理与负载均衡](#6-nginx-反向代理与负载均衡)
7. [Docker 容器化](#7-docker-容器化)
8. [Kubernetes 部署](#8-kubernetes-部署)
9. [Jenkins CI/CD 自动化流水线](#9-jenkins-cicd-自动化流水线)
10. [监控与日志](#10-监控与日志)

---

## 1. 架构总览

### 1.1 整体架构图

```
                          ┌──────────────┐
                          │   DNS / CDN   │
                          └──────┬───────┘
                                 │
                          ┌──────▼───────┐
                          │  Nginx Ingress│ (K8s)
                          └──────┬───────┘
                                 │
                    ┌────────────┼────────────┐
                    │            │            │
            ┌───────▼──────┐ ┌──▼──────┐ ┌───▼──────┐
            │  Django App  │ │ Django  │ │ Django   │
            │  Pod Replica │ │  Pod 2  │ │  Pod N   │
            └───────┬──────┘ └───┬─────┘ └────┬─────┘
                    │            │            │
                    └────────────┼────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
     ┌────────▼──────┐  ┌───────▼──────┐  ┌────────▼────┐
     │  MySQL Master │  │ MySQL Slave  │  │ MySQL Shard │
     │   (Shard 0)   │  │   (Shard 1)  │  │   (Shard N) │
     └───────────────┘  └──────────────┘  └─────────────┘
              │
     ┌────────▼──────┐
     │ Redis Cluster │  (Session + Cache + Queue)
     └───────────────┘
```

### 1.2 技术选型说明

| 组件 | 版本 | 用途 |
|------|------|------|
| Python | 3.11 | 后端开发语言 |
| Django | 4.2 LTS | Web 框架 |
| Django REST Framework | 3.14 | RESTful API |
| Celery | 5.3 | 异步任务队列 |
| MySQL | 8.0 | 关系型数据库（分库分表） |
| Redis | 7.0 | 缓存 / Session / 消息队列 |
| Nginx | 1.25 | 反向代理 / 负载均衡 / 静态资源 |
| Docker | 24.x | 容器化 |
| Kubernetes | 1.28 | 容器编排 |
| Jenkins | 2.426 LTS | CI/CD 自动化 |

### 1.3 项目目录结构

```
enterprise-platform/
├── src/
│   ├── config/                    # Django 配置
│   │   ├── __init__.py
│   │   ├── settings/
│   │   │   ├── __init__.py
│   │   │   ├── base.py            # 基础配置
│   │   │   ├── dev.py             # 开发环境
│   │   │   ├── staging.py         # 预发布环境
│   │   │   └── production.py      # 生产环境
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── apps/                      # 业务应用
│   │   ├── user/                  # 用户模块
│   │   ├── order/                 # 订单模块（分库示例）
│   │   └── product/               # 商品模块
│   ├── middleware/                 # 中间件
│   ├── utils/                     # 工具类
│   │   ├── db_router.py           # 数据库路由
│   │   ├── redis_client.py        # Redis 客户端
│   │   └── sharding.py            # 分库分表工具
│   ├── tasks/                     # Celery 任务
│   └── manage.py
├── deploy/
│   ├── docker/
│   │   ├── Dockerfile
│   │   └── docker-compose.yml
│   ├── k8s/
│   │   ├── namespace.yaml
│   │   ├── configmap.yaml
│   │   ├── secret.yaml
│   │   ├── django-deployment.yaml
│   │   ├── django-service.yaml
│   │   ├── django-hpa.yaml
│   │   ├── mysql-statefulset.yaml
│   │   ├── redis-statefulset.yaml
│   │   ├── nginx-deployment.yaml
│   │   ├── ingress.yaml
│   │   └── pvc.yaml
│   └── jenkins/
│       └── Jenkinsfile
├── scripts/
│   ├── init_sharding.sql
│   ├── migrate.sh
│   └── backup.sh
├── requirements.txt
├── pytest.ini
└── Makefile
```

---

## 2. 环境准备

### 2.1 服务器规划

| 角色 | 主机名 | IP 地址 | 配置 | 操作系统 |
|------|--------|---------|------|---------|
| K8s Master 1 | k8s-master-01 | 10.0.1.11 | 4C/8G/100G SSD | Ubuntu 22.04 LTS |
| K8s Master 2 | k8s-master-02 | 10.0.1.12 | 4C/8G/100G SSD | Ubuntu 22.04 LTS |
| K8s Master 3 | k8s-master-03 | 10.0.1.13 | 4C/8G/100G SSD | Ubuntu 22.04 LTS |
| K8s Worker 1 | k8s-worker-01 | 10.0.1.21 | 8C/16G/200G SSD | Ubuntu 22.04 LTS |
| K8s Worker 2 | k8s-worker-02 | 10.0.1.22 | 8C/16G/200G SSD | Ubuntu 22.04 LTS |
| K8s Worker 3 | k8s-worker-03 | 10.0.1.23 | 8C/16G/200G SSD | Ubuntu 22.04 LTS |
| MySQL 主库 | mysql-master | 10.0.2.11 | 8C/32G/500G SSD | Ubuntu 22.04 LTS |
| MySQL 从库 | mysql-slave | 10.0.2.12 | 8C/32G/500G SSD | Ubuntu 22.04 LTS |
| MySQL 分片 0~3 | mysql-shard-0~3 | 10.0.2.21~24 | 4C/16G/200G SSD×4 | Ubuntu 22.04 LTS |
| Redis 节点 0~2 | redis-node-0~2 | 10.0.3.11~13 | 4C/16G/100G SSD | Ubuntu 22.04 LTS |
| Harbor 仓库 | harbor-registry | 10.0.4.11 | 4C/8G/200G SSD | Ubuntu 22.04 LTS |
| Jenkins | jenkins-server | 10.0.4.21 | 4C/8G/200G SSD | Ubuntu 22.04 LTS |
| NFS 存储 | nfs-storage | 10.0.4.31 | 4C/8G/500G HDD | Ubuntu 22.04 LTS |

### 2.2 所有服务器基础初始化（每台服务器执行）

```bash
# ============================================
# 以 root 用户登录每台服务器，执行以下初始化
# ============================================

# 1. 设置主机名（根据规划修改）
hostnamectl set-hostname k8s-master-01     # 示例：第一台 Master

# 2. 配置静态 IP（修改 /etc/netplan/00-installer-config.yaml）
cat > /etc/netplan/00-installer-config.yaml <<EOF
network:
  ethernets:
    eth0:
      addresses:
        - 10.0.1.11/24     # 根据实际 IP 修改
      routes:
        - to: default
          via: 10.0.1.1    # 网关
      nameservers:
        addresses: [223.5.5.5, 8.8.8.8]
  version: 2
EOF

netplan apply

# 3. 关闭 swap（K8s 要求）
swapoff -a
sed -i '/swap/d' /etc/fstab

# 4. 关闭 SELinux / AppArmor
# Ubuntu 默认无 SELinux，如 CentOS 需执行:
# setenforce 0 && sed -i 's/^SELINUX=enforcing/SELINUX=disabled/' /etc/selinux/config

# 5. 关闭防火墙（生产环境建议用 iptables 规则替代）
ufw disable

# 6. 配置内核参数
cat >> /etc/sysctl.d/k8s.conf <<EOF
net.bridge.bridge-nf-call-iptables  = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.ip_forward                 = 1
net.ipv4.tcp_tw_recycle             = 0
vm.swappiness                       = 0
vm.overcommit_memory                = 1
vm.panic_on_oom                     = 0
fs.inotify.max_user_instances       = 8192
fs.inotify.max_user_watches         = 1048576
fs.file-max                         = 52706963
fs.nr_open                          = 52706963
net.ipv6.conf.all.disable_ipv6      = 1
net.netfilter.nf_conntrack_max      = 2310720
EOF

sysctl --system

# 7. 安装基础工具
apt update && apt install -y \
    curl wget git vim htop net-tools \
    ca-certificates gnupg lsb-release \
    apt-transport-https software-properties-common \
    conntrack ipvsadm ipset jq sysstat \
    nfs-common cifs-utils

# 8. 配置 hosts 文件（所有服务器统一）
cat >> /etc/hosts <<EOF
# K8s Cluster
10.0.1.11  k8s-master-01
10.0.1.12  k8s-master-02
10.0.1.13  k8s-master-03
10.0.1.21  k8s-worker-01
10.0.1.22  k8s-worker-02
10.0.1.23  k8s-worker-03
# MySQL
10.0.2.11  mysql-master
10.0.2.12  mysql-slave
10.0.2.21  mysql-shard-0
10.0.2.22  mysql-shard-1
10.0.2.23  mysql-shard-2
10.0.2.24  mysql-shard-3
# Redis
10.0.3.11  redis-node-0
10.0.3.12  redis-node-1
10.0.3.13  redis-node-2
# Infrastructure
10.0.4.11  harbor-registry
10.0.4.21  jenkins-server
10.0.4.31  nfs-storage
EOF

# 9. 配置时间同步
apt install -y chrony
systemctl enable chrony --now
chronyc sources
```

### 2.3 Docker CE 安装（所有 K8s 节点 + Harbor + Jenkins 服务器）

```bash
# ============================================
# 在所有需要 Docker 的服务器上执行
# ============================================

# 1. 卸载旧版本（如有）
apt remove -y docker docker-engine docker.io containerd runc

# 2. 安装 Docker GPG Key 和仓库
mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null

# 3. 安装 Docker CE
apt update && apt install -y \
    docker-ce docker-ce-cli containerd.io \
    docker-buildx-plugin docker-compose-plugin

# 4. 配置 Docker daemon
mkdir -p /etc/docker
cat > /etc/docker/daemon.json <<'EOF'
{
  "exec-opts": ["native.cgroupdriver=systemd"],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m",
    "max-file": "3"
  },
  "storage-driver": "overlay2",
  "storage-opts": [
    "overlay2.override_kernel_check=true"
  ],
  "registry-mirrors": [
    "https://mirror.ccs.tencentyun.com"
  ],
  "insecure-registries": ["harbor-registry:8443"],
  "data-root": "/var/lib/docker",
  "live-restore": true,
  "max-concurrent-downloads": 10
}
EOF

systemctl daemon-reload
systemctl enable docker --now
systemctl status docker

# 5. 安装 Docker Compose（独立二进制，备用）
curl -L "https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-$(uname -s)-$(uname -m)" \
    -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# 6. 验证
docker --version          # Docker version 24.0.7
docker compose version    # Docker Compose version v2.23.0
docker run --rm hello-world
```

### 2.4 K8s 集群部署（kubeadm）

#### 2.4.1 安装 kubeadm/kubelet/kubectl（所有 K8s 节点）

```bash
# ============================================
# 在所有 K8s 节点（Master + Worker）执行
# ============================================

# 1. 安装 Kubernetes 组件
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.28/deb/Release.key | \
    gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg

echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] \
    https://pkgs.k8s.io/core:/stable:/v1.28/deb/ /' | \
    tee /etc/apt/sources.list.d/kubernetes.list

apt update && apt install -y kubelet=1.28.3-1.1 kubeadm=1.28.3-1.1 kubectl=1.28.3-1.1
apt-mark hold kubelet kubeadm kubectl  # 防止意外升级

# 3. 安装 Helm（K8s 包管理器，NFS CSI Driver/cert-manager 等都需要）
curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
helm version  # v3.13.x

# 2. 配置 kubelet
cat > /etc/default/kubelet <<EOF
KUBELET_EXTRA_ARGS="--cgroup-driver=systemd --runtime-cgroups=/systemd/system.slice --kubelet-cgroups=/systemd/system.slice"
EOF

systemctl enable kubelet
```

#### 2.4.2 配置 containerd（所有 K8s 节点）

```bash
# ============================================
# 在所有 K8s 节点执行 — K8s 1.28 默认使用 containerd 作为 CRI
# ============================================

# 1. 生成 containerd 默认配置
mkdir -p /etc/containerd
containerd config default > /etc/containerd/config.toml

# 2. 关键修改: 启用 SystemdCgroup
sed -i 's|SystemdCgroup = false|SystemdCgroup = true|g' /etc/containerd/config.toml

# 3. 替换 sandbox_image 为国内镜像（解决 gcr.io 拉取失败）
sed -i 's|sandbox_image = "registry.k8s.io/pause:3.9"|sandbox_image = "registry.aliyuncs.com/google_containers/pause:3.9"|g' /etc/containerd/config.toml

# 4. 重启 containerd
systemctl restart containerd
systemctl status containerd

# 5. 验证 CRI 可用
crictl version
# Version:  v1.28.x
# RuntimeName:  containerd
crictl images
```

#### 2.4.3 初始化第一个 Master 节点

```bash
# ============================================
# 仅在 k8s-master-01 执行
# ============================================

# 1. 创建 kubeadm 配置文件
cat > /root/kubeadm-config.yaml <<EOF
apiVersion: kubeadm.k8s.io/v1beta3
kind: InitConfiguration
localAPIEndpoint:
  advertiseAddress: 10.0.1.11     # Master-01 IP
  bindPort: 6443
nodeRegistration:
  criSocket: unix:///var/run/containerd/containerd.sock
  name: k8s-master-01
  taints:
    - key: node-role.kubernetes.io/control-plane
      effect: NoSchedule
---
apiVersion: kubeadm.k8s.io/v1beta3
kind: ClusterConfiguration
kubernetesVersion: v1.28.3
controlPlaneEndpoint: "10.0.1.100:6443"   # 虚拟 IP (Keepalived)
imageRepository: registry.aliyuncs.com/google_containers
networking:
  serviceSubnet: "10.96.0.0/12"
  podSubnet: "10.244.0.0/16"
  dnsDomain: "cluster.local"
apiServer:
  certSANs:
    - "k8s-api.example.com"
    - "10.0.1.11"
    - "10.0.1.12"
    - "10.0.1.13"
    - "10.0.1.100"
  extraArgs:
    audit-log-path: "/var/log/kubernetes/audit.log"
    audit-log-maxage: "30"
    audit-log-maxbackup: "10"
    audit-log-maxsize: "100"
controllerManager:
  extraArgs:
    bind-address: "0.0.0.0"
scheduler:
  extraArgs:
    bind-address: "0.0.0.0"
---
apiVersion: kubeproxy.config.k8s.io/v1alpha1
kind: KubeProxyConfiguration
mode: ipvs
ipvs:
  scheduler: "rr"
EOF

# 2. 拉取镜像
kubeadm config images pull --config /root/kubeadm-config.yaml

# 3. 初始化集群
kubeadm init --config /root/kubeadm-config.yaml --upload-certs

# 4. 配置 kubectl
mkdir -p $HOME/.kube
cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
chown $(id -u):$(id -g) $HOME/.kube/config

# 保存 join 命令（后续加入节点用）
# 输出类似:
# kubeadm join 10.0.1.100:6443 --token xxx --discovery-token-ca-cert-hash sha256:xxx --control-plane --certificate-key xxx  (Master 加入)
# kubeadm join 10.0.1.100:6443 --token xxx --discovery-token-ca-cert-hash sha256:xxx  (Worker 加入)
```

#### 2.4.3 安装 Calico 网络插件

```bash
# ============================================
# 在 k8s-master-01 执行
# ============================================

# 下载并修改 Calico 配置
curl -O https://raw.githubusercontent.com/projectcalico/calico/v3.26.0/manifests/calico.yaml

# 修改 Pod 网段（确保与 kubeadm 配置一致: 10.244.0.0/16）
# 取消注释 CALICO_IPV4POOL_CIDR 并设置为 10.244.0.0/16
sed -i 's|# - name: CALICO_IPV4POOL_CIDR|- name: CALICO_IPV4POOL_CIDR|' calico.yaml
sed -i 's|#   value: "192.168.0.0/16"|  value: "10.244.0.0/16"|' calico.yaml

kubectl apply -f calico.yaml

# 验证
kubectl get pods -n calico-system
kubectl get nodes    # 应显示 Ready
```

#### 2.4.5 配置 Keepalived + HAProxy（VIP 高可用）

> **说明**: `controlPlaneEndpoint` 指定的 VIP `10.0.1.100` 需要一个反向代理把请求转发到三个 Master 的 apiserver 6443 端口。

在三个 Master 节点上**分别执行**：

```bash
# ============================================
# 在 k8s-master-01/02/03 分别执行
# ============================================

# 1. 安装 Keepalived + HAProxy
apt install -y keepalived haproxy

# 2. 配置 HAProxy（三台一致）
cat > /etc/haproxy/haproxy.cfg <<'EOF'
global
    maxconn 2000
    log /dev/log local0

defaults
    mode tcp
    timeout connect 5s
    timeout client 30s
    timeout server 30s
    retries 3

frontend k8s-api
    bind *:6443
    default_backend k8s-masters

backend k8s-masters
    balance roundrobin
    option tcp-check
    server master-01 10.0.1.11:6443 check fall 3 rise 2
    server master-02 10.0.1.12:6443 check fall 3 rise 2
    server master-03 10.0.1.13:6443 check fall 3 rise 2
EOF

systemctl enable haproxy --now
systemctl status haproxy

# 3. 自动检测主网卡名（不写死 eth0，兼容 ens192/ens33/enp0s3 等）
PRIMARY_NIC=$(ip route show default | awk '/default/ {print $5}')
echo "Detected primary NIC: ${PRIMARY_NIC}"

# 配置 Keepalived（每台 priority 不同！）
# --- k8s-master-01 (MASTER) ---
cat > /etc/keepalived/keepalived.conf <<EOF
vrrp_instance VI_1 {
    state MASTER
    interface ${PRIMARY_NIC}
    virtual_router_id 51
    priority 100               # Master-01 最高
    advert_int 1
    authentication {
        auth_type PASS
        auth_pass K8sVip2024
    }
    virtual_ipaddress {
        10.0.1.100/24 dev ${PRIMARY_NIC}
    }
}
EOF

# --- k8s-master-02 (BACKUP, priority=90) ---
# 复制上述配置后，执行:
# sed -i 's/state MASTER/state BACKUP/;s/priority 100/priority 90/' /etc/keepalived/keepalived.conf

# --- k8s-master-03 (BACKUP, priority=80) ---
# sed -i 's/state MASTER/state BACKUP/;s/priority 100/priority 80/' /etc/keepalived/keepalived.conf

systemctl enable keepalived --now

# 4. 验证 VIP
ip addr show eth0 | grep 10.0.1.100
# 应显示在 Master-01 上
```

#### 2.4.6 加入其余 Master 节点（控制平面高可用）

```bash
# ============================================
# 在 k8s-master-02 和 k8s-master-03 分别执行
# ============================================

# 使用初始化时输出的 control-plane join 命令
kubeadm join 10.0.1.100:6443 \
  --token <token> \
  --discovery-token-ca-cert-hash sha256:<hash> \
  --control-plane \
  --certificate-key <cert-key>

# 配置 kubectl
mkdir -p $HOME/.kube
cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
```

#### 2.4.7 加入 Worker 节点

```bash
# ============================================
# 在 k8s-worker-01/02/03 分别执行
# ============================================

# 使用加入命令
kubeadm join 10.0.1.100:6443 \
  --token <token> \
  --discovery-token-ca-cert-hash sha256:<hash>

# 如果 token 过期，在 Master 上重新生成:
# kubeadm token create --print-join-command
```

#### 2.4.8 安装 MetalLB（LoadBalancer，裸金属必备）

```bash
# ============================================
# 在 k8s-master-01 执行
# ============================================

# 在没有云厂商 LB 的裸金属服务器上，用 MetalLB 提供 LoadBalancer 服务
kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/v0.13.12/config/manifests/metallb-native.yaml

# 等待 MetalLB 就绪
kubectl wait --namespace metallb-system \
    --for=condition=ready pod \
    --selector=app=metallb \
    --timeout=90s

# 配置 IP 池（与 K8s 节点同网段的空闲 IP 段）
cat <<EOF | kubectl apply -f -
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: default-pool
  namespace: metallb-system
spec:
  addresses:
    - 10.0.1.200-10.0.1.250    # 用于 LoadBalancer Service 的 IP 池
---
apiVersion: metallb.io/v1beta1
kind: L2Advertisement
metadata:
  name: default-l2
  namespace: metallb-system
spec:
  ipAddressPools:
    - default-pool
EOF
```

#### 2.4.9 安装 cert-manager（Let's Encrypt 自动签发 TLS 证书）

```bash
# ============================================
# 在 k8s-master-01 执行
# ============================================

# 1. 安装 cert-manager CRD 和控制器
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.3/cert-manager.yaml

# 2. 等待 cert-manager 就绪
kubectl wait --namespace cert-manager \
    --for=condition=ready pod \
    --selector=app.kubernetes.io/instance=cert-manager \
    --timeout=120s

# 3. 创建 Let's Encrypt ClusterIssuer（生产版）
cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@example.com               # 改为真实邮箱
    privateKeySecretRef:
      name: letsencrypt-prod-key
    solvers:
      - http01:
          ingress:
            class: nginx
EOF

# 4. 验证
kubectl get clusterissuer letsencrypt-prod -o wide
# READY=True

# 测试: 部署一个测试 Ingress 验证证书自动签发
cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: cert-test
  namespace: default
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
    - hosts:
        - test.example.com
      secretName: test-tls-cert
  rules:
    - host: test.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: nginx-test
                port:
                  number: 80
EOF

# 验证证书签发
kubectl get certificates -A
kubectl describe certificate test-tls-cert -n default
```

#### 2.4.10 安装 Nginx Ingress Controller

```bash
# ============================================
# 在 k8s-master-01 执行
# ============================================

kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.9.0/deploy/static/provider/baremetal/deploy.yaml

# 修改 Ingress Controller Service 为 LoadBalancer 类型
kubectl patch service ingress-nginx-controller \
    -n ingress-nginx \
    -p '{"spec": {"type": "LoadBalancer"}}'

# 查看分配的 External IP
kubectl get svc -n ingress-nginx ingress-nginx-controller
# EXTERNAL-IP: 10.0.1.200 (MetalLB 自动分配)
```

#### 2.4.11 验证集群

```bash
# ============================================
# 在 k8s-master-01 执行验证
# ============================================

kubectl get nodes -o wide
# 期望: 6 个节点全部 Ready

kubectl get pods -A
# 所有 Pod Running

# 部署测试应用
kubectl create deployment nginx-test --image=nginx:alpine
kubectl expose deployment nginx-test --port=80 --type=LoadBalancer
kubectl get svc nginx-test
# 应分配 EXTERNAL-IP

# 清理测试
kubectl delete deployment nginx-test
kubectl delete svc nginx-test
```

### 2.5 Harbor 私有镜像仓库部署

```bash
# ============================================
# 在 harbor-registry (10.0.4.11) 执行
# ============================================

# 1. 下载 Harbor
cd /opt
curl -L https://github.com/goharbor/harbor/releases/download/v2.9.0/harbor-offline-installer-v2.9.0.tgz \
    -o harbor.tgz
tar xzf harbor.tgz
cd harbor

# 2. 配置 harbor.yml
cp harbor.yml.tmpl harbor.yml
cat > harbor.yml <<EOF
hostname: harbor-registry
http:
  port: 80
https:
  port: 8443
  certificate: /opt/harbor/certs/harbor.crt
  private_key: /opt/harbor/certs/harbor.key

harbor_admin_password: Harbor12345

database:
  password: root123
  max_idle_conns: 100
  max_open_conns: 900

data_volume: /data/harbor

log:
  level: info
  local:
    rotate_count: 50
    rotate_size: 200M
  external_endpoint: http://harbor-registry

jobservice:
  max_job_workers: 10

notification:
  webhook_job_max_retry: 10

chart:
  absolute_url: disabled

trivy:
  ignore_unfixed: false
  skip_update: false
  insecure: false
EOF

# 3. 生成自签名证书
mkdir -p /opt/harbor/certs
openssl req -newkey rsa:4096 -nodes -sha256 \
    -keyout /opt/harbor/certs/harbor.key \
    -x509 -days 3650 \
    -out /opt/harbor/certs/harbor.crt \
    -subj "/C=CN/ST=Beijing/L=Beijing/O=Company/CN=harbor-registry" \
    -addext "subjectAltName=DNS:harbor-registry,IP:10.0.4.11"

# 4. 安装 Harbor
./install.sh --with-trivy --with-chartmuseum

# 5. 在所有 K8s 节点和 Jenkins 服务器上信任证书
# （在 Harbor 服务器上拷贝证书到各节点）
for node in k8s-master-01 k8s-master-02 k8s-master-03 \
            k8s-worker-01 k8s-worker-02 k8s-worker-03 \
            jenkins-server; do
    scp /opt/harbor/certs/harbor.crt root@${node}:/usr/local/share/ca-certificates/harbor.crt
    ssh root@${node} "update-ca-certificates && systemctl restart docker"
done

# 6. 验证
docker login harbor-registry:8443 -u admin -p Harbor12345

# 7. 创建项目
# 浏览器访问 https://10.0.4.11:8443
# 创建项目: enterprise-platform (用于存放应用镜像)
```

### 2.6 Jenkins 服务器部署

```bash
# ============================================
# 在 jenkins-server (10.0.4.21) 执行
# ============================================

# 1. 创建 Jenkins 持久化目录
mkdir -p /data/jenkins
chown 1000:1000 /data/jenkins    # Jenkins 容器内用户 UID=1000

# 2. 使用 Docker Compose 启动 Jenkins
mkdir -p /opt/jenkins
cat > /opt/jenkins/docker-compose.yml <<EOF
version: '3.8'

services:
  jenkins:
    image: jenkins/jenkins:2.426-lts
    container_name: jenkins
    restart: unless-stopped
    ports:
      - "8080:8080"
      - "50000:50000"
    environment:
      JAVA_OPTS: "-Djenkins.install.runSetupWizard=true -Xms2g -Xmx4g"
    volumes:
      - /data/jenkins:/var/jenkins_home
      # 安全: 不挂载 docker.sock（避免容器逃逸风险），
      # 构建镜像使用 Kaniko（无需 Docker daemon，无特权模式）
      - /usr/local/bin/kubectl:/usr/local/bin/kubectl    # 挂载 kubectl
      - /root/.kube/config:/root/.kube/config:ro          # 挂载 kubeconfig
    extra_hosts:
      - "harbor-registry:10.0.4.11"   # Harbor 域名解析
EOF

cd /opt/jenkins && docker compose up -d

# 3. 获取初始密码
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword

# 4. 访问 Jenkins
# http://10.0.4.21:8080
# 输入初始密码 → 安装推荐插件 → 创建管理员账户

# 5. 安装必要插件（Jenkins → Manage Jenkins → Plugins）
# 必须安装:
#   - Docker Pipeline
#   - Kubernetes CLI
#   - Kubernetes Client API
#   - Git Parameter
#   - Blue Ocean
#   - Pipeline Utility Steps
#   - Slack Notification
#   - SonarQube Scanner

# 6. 配置凭据（Jenkins → Manage Jenkins → Credentials）
# - Harbor 仓库凭据: 类型 "Username with password", ID "harbor-credentials"
#   Username: admin, Password: Harbor12345
# - K8s kubeconfig: 类型 "Secret file", ID "k8s-config"
#   上传 /root/.kube/config
# - GitHub Token: 类型 "Secret text", ID "github-token"
# - Slack Webhook: 类型 "Secret text", ID "slack-webhook-url"
```

### 2.7 NFS 共享存储部署

```bash
# ============================================
# 在 nfs-storage (10.0.4.31) 执行
# ============================================

# 1. 安装 NFS 服务端
apt install -y nfs-kernel-server

# 2. 创建共享目录
mkdir -p /data/nfs/{static,media,backup,general}
chown -R nobody:nogroup /data/nfs

# 3. 配置 exports
cat >> /etc/exports <<EOF
/data/nfs/static   *(rw,sync,no_root_squash,no_subtree_check)
/data/nfs/media    *(rw,sync,no_root_squash,no_subtree_check)
/data/nfs/backup   *(rw,sync,no_root_squash,no_subtree_check)
/data/nfs/general  *(rw,sync,no_root_squash,no_subtree_check)
EOF

# 4. 重启并验证
exportfs -a
systemctl enable nfs-kernel-server --now
systemctl status nfs-kernel-server
showmount -e 127.0.0.1

# 5. 安装 NFS CSI Driver（在 K8s Master 执行）
#    这是 K8s 使用 NFS 的前置条件，没有这个 Driver，PVC 会一直 Pending
helm repo add csi-driver-nfs https://raw.githubusercontent.com/kubernetes-csi/csi-driver-nfs/master/charts
helm upgrade --install csi-driver-nfs csi-driver-nfs/csi-driver-nfs \
    --namespace kube-system \
    --set kubeletDir=/var/lib/kubelet

# 等待 Driver 就绪
kubectl wait --for=condition=ready pod \
    -l app=csi-nfs-controller -n kube-system --timeout=120s
kubectl get pods -n kube-system | grep csi-nfs

# 6. 创建 NFS StorageClass
kubectl apply -f - <<EOF
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: nfs-storage
provisioner: nfs.csi.k8s.io
parameters:
  server: 10.0.4.31
  share: /data/nfs
mountOptions:
  - hard
  - nfsvers=4.1
reclaimPolicy: Retain
volumeBindingMode: Immediate
EOF

echo "NFS storage setup complete."
```

---

## 3. Django 后端应用开发

### 3.1 创建 Django 项目

```bash
mkdir -p ~/enterprise-platform && cd ~/enterprise-platform
python3.11 -m venv venv
source venv/bin/activate

pip install django==4.2.11 djangorestframework==3.14.0 celery==5.3.6 \
    redis==5.0.1 mysqlclient==2.2.4 gunicorn==21.2.0 \
    django-cors-headers==4.3.1 whitenoise==6.6.0 \
    djangorestframework-simplejwt==5.3.1 \
    django-redis==5.4.0 channels==4.1.0

mkdir -p src
django-admin startproject config src
cd src
python manage.py startapp user
python manage.py startapp order
python manage.py startapp product
```

### 3.2 多环境配置

**`src/config/settings/__init__.py`**

```python
import os

ENV = os.environ.get('DJANGO_ENV', 'dev')

if ENV == 'production':
    from .production import *
elif ENV == 'staging':
    from .staging import *
else:
    from .dev import *
```

**`src/config/settings/base.py`**

```python
import os
from pathlib import Path
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'dev-secret-change-in-production')

DEBUG = False

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 第三方
    'rest_framework',
    'corsheaders',
    'django_celery_results',
    # 业务应用
    'apps.user',
    'apps.order',
    'apps.product',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    # Whitenoise: 高效 serve 静态文件（DEBUG=False 时 Django 不 serve static）
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'middleware.request_log.RequestLogMiddleware',
    'middleware.tracing.TracingMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Whitenoise: 压缩 + 永久缓存（指纹化文件名）
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
    },
    'EXCEPTION_HANDLER': 'utils.exceptions.custom_exception_handler',
}

# JWT
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'AUDIENCE': 'enterprise-platform',
}

# Celery
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = 'django-db'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Shanghai'
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 min
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60

# CORS
CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000').split(',')

# 日志
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'json': {
            'format': '{"time":"%(asctime)s","level":"%(levelname)s","module":"%(module)s","message":"%(message)s"}',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django.log'),
            'maxBytes': 100 * 1024 * 1024,  # 100MB
            'backupCount': 10,
            'formatter': 'json',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': os.environ.get('LOG_LEVEL', 'INFO'),
    },
}
```

**`src/config/settings/production.py`**

```python
import os
from .base import *

DEBUG = False

# 生产数据库 - 使用读写分离 + 分库
DATABASES = {
    # 默认库 - 用户/配置等公共数据
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', 'enterprise_platform'),
        'USER': os.environ.get('DB_USER', 'root'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'mysql-master'),
        'PORT': os.environ.get('DB_PORT', '3306'),
        'CONN_MAX_AGE': 600,
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'connect_timeout': 10,
        },
    },
    'default_read': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', 'enterprise_platform'),
        'USER': os.environ.get('DB_USER', 'root'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_READ_HOST', 'mysql-slave'),
        'PORT': os.environ.get('DB_PORT', '3306'),
        'CONN_MAX_AGE': 600,
        'OPTIONS': {'charset': 'utf8mb4'},
    },
    # 订单库 - 分片 0
    'order_shard_0': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'enterprise_order_0',
        'USER': os.environ.get('DB_USER', 'root'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_SHARD0_HOST', 'mysql-shard-0'),
        'PORT': os.environ.get('DB_PORT', '3306'),
        'CONN_MAX_AGE': 600,
        'OPTIONS': {'charset': 'utf8mb4'},
    },
    'order_shard_1': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'enterprise_order_1',
        'USER': os.environ.get('DB_USER', 'root'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_SHARD1_HOST', 'mysql-shard-1'),
        'PORT': os.environ.get('DB_PORT', '3306'),
        'CONN_MAX_AGE': 600,
        'OPTIONS': {'charset': 'utf8mb4'},
    },
    'order_shard_2': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'enterprise_order_2',
        'USER': os.environ.get('DB_USER', 'root'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_SHARD2_HOST', 'mysql-shard-2'),
        'PORT': os.environ.get('DB_PORT', '3306'),
        'CONN_MAX_AGE': 600,
        'OPTIONS': {'charset': 'utf8mb4'},
    },
    'order_shard_3': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'enterprise_order_3',
        'USER': os.environ.get('DB_USER', 'root'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_SHARD3_HOST', 'mysql-shard-3'),
        'PORT': os.environ.get('DB_PORT', '3306'),
        'CONN_MAX_AGE': 600,
        'OPTIONS': {'charset': 'utf8mb4'},
    },
}

# 数据库路由
DATABASE_ROUTERS = [
    'utils.db_router.MasterSlaveRouter',
    'utils.db_router.OrderShardRouter',
]

# Redis 集群
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': [
            'redis://redis-node-0:6379/1',
            'redis://redis-node-1:6379/1',
            'redis://redis-node-2:6379/1',
        ],
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_CLASS': 'redis.connection.BlockingConnectionPool',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'timeout': 20,
            },
            'PASSWORD': os.environ.get('REDIS_PASSWORD', ''),
        },
    }
}

# Session 使用 Redis
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 86400  # 24h

# Celery Broker - Redis
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://redis-cluster-service:6379/0')

# 安全配置
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# 静态文件 - 使用 CDN
STATIC_URL = os.environ.get('STATIC_URL', 'https://cdn.example.com/static/')

# Sentry
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration

sentry_sdk.init(
    dsn=os.environ.get('SENTRY_DSN', ''),
    integrations=[DjangoIntegration(), CeleryIntegration()],
    traces_sample_rate=float(os.environ.get('SENTRY_TRACES_RATE', 0.1)),
    environment='production',
    send_default_pii=False,
)
```

### 3.3 中间件实现

**`src/middleware/request_log.py`**

```python
import logging
import time
import json

logger = logging.getLogger(__name__)


class RequestLogMiddleware:
    """请求日志中间件"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()

        response = self.get_response(request)

        duration = time.time() - start_time

        log_data = {
            'method': request.method,
            'path': request.path,
            'status_code': response.status_code,
            'duration_ms': round(duration * 1000, 2),
            'user_id': request.user.id if request.user.is_authenticated else None,
            'remote_addr': self._get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', '')[:200],
        }

        if response.status_code >= 500:
            logger.error(f'Request: {json.dumps(log_data, ensure_ascii=False)}')
        elif response.status_code >= 400:
            logger.warning(f'Request: {json.dumps(log_data, ensure_ascii=False)}')
        else:
            logger.info(f'Request: {json.dumps(log_data, ensure_ascii=False)}')

        response['X-Request-Time'] = str(duration)
        response['X-Request-ID'] = getattr(request, 'request_id', '')

        return response

    @staticmethod
    def _get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '')
```

**`src/middleware/tracing.py`**

```python
import uuid


class TracingMiddleware:
    """分布式链路追踪中间件 - 注入 trace_id"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        trace_id = request.META.get('HTTP_X_TRACE_ID', request.META.get('HTTP_X_REQUEST_ID', str(uuid.uuid4())))
        request.trace_id = trace_id
        request.request_id = str(uuid.uuid4())

        response = self.get_response(request)

        response['X-Trace-ID'] = trace_id
        response['X-Request-ID'] = request.request_id

        return response
```

### 3.4 数据库路由

**`src/utils/db_router.py`**

```python
import random


class MasterSlaveRouter:
    """
    读写分离路由
    - 写操作 → default (Master)
    - 读操作 → default_read (Slave)
    """

    def db_for_read(self, model, **hints):
        if model._meta.app_label in ('auth', 'admin', 'contenttypes', 'sessions'):
            return 'default'
        return 'default_read'

    def db_for_write(self, model, **hints):
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        db_set = {obj1._state.db, obj2._state.db}
        if None in db_set:
            return True
        return len(db_set) == 1

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if db == 'default_read':
            return False
        return True


class OrderShardRouter:
    """
    订单分库路由
    - 根据 user_id 取模决定分片
    - 4 个分片: order_shard_0 ~ order_shard_3
    """

    SHARD_COUNT = 4
    SHARD_PREFIX = 'order_shard'

    def _get_shard(self, model, **hints):
        """根据 hint 中的 user_id 或 instance 计算分片"""
        if hints.get('instance'):
            instance = hints['instance']
            user_id = getattr(instance, 'user_id', None)
            if user_id:
                shard_id = user_id % self.SHARD_COUNT
                return f'{self.SHARD_PREFIX}_{shard_id}'
        if hints.get('user_id') is not None:
            user_id = hints['user_id']
            shard_id = user_id % self.SHARD_COUNT
            return f'{self.SHARD_PREFIX}_{shard_id}'
        return None

    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'order':
            shard = self._get_shard(model, **hints)
            if shard:
                return shard
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'order':
            shard = self._get_shard(model, **hints)
            if shard:
                return shard
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == 'order' or obj2._meta.app_label == 'order':
            return obj1._state.db == obj2._state.db
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'order':
            return db.startswith(self.SHARD_PREFIX)
        return None
```

### 3.5 订单模块（分库示例）

**`src/apps/order/models.py`**

```python
from django.db import models


class Order(models.Model):
    """
    订单模型 — 使用分库路由存储

    数据分布: user_id % 4 → order_shard_{0..3}
    """
    STATUS_CHOICES = [
        ('pending', '待支付'),
        ('paid', '已支付'),
        ('shipped', '已发货'),
        ('delivered', '已送达'),
        ('cancelled', '已取消'),
        ('refunded', '已退款'),
    ]

    user_id = models.BigIntegerField(db_index=True, verbose_name='用户ID')
    order_no = models.CharField(max_length=32, unique=True, verbose_name='订单编号')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='总金额')
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='优惠金额')
    actual_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='实付金额')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True, verbose_name='订单状态')
    remark = models.TextField(blank=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'order_info'
        ordering = ['-created_at']

    def __str__(self):
        return f'Order({self.order_no})'


class OrderItem(models.Model):
    """订单商品明细"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_id = models.BigIntegerField(verbose_name='商品ID')
    product_name = models.CharField(max_length=255, verbose_name='商品名称')
    quantity = models.IntegerField(verbose_name='数量')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='单价')
    total_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='小计')

    class Meta:
        db_table = 'order_item'
```

**`src/apps/order/services.py`**

```python
"""
订单服务层 - 处理分库写入逻辑
"""
from django.db import transaction
from django.db.models import Sum
from apps.order.models import Order, OrderItem


class OrderService:

    @staticmethod
    @transaction.atomic
    def create_order(user_id: int, items_data: list, remark: str = '') -> Order:
        """创建订单 - 直接计算分片路由

        注意: 不能使用 Order.objects.create() 期望 router 自动路由，
        因为 Django ORM 的 create() 不会将字段值作为 hints 传给 router。
        正确做法是自行计算分片，显式 using(shard)。
        """
        import time
        order_no = f"ORD{int(time.time() * 1000)}{user_id % 10000:04d}"

        total = sum(item['unit_price'] * item['quantity'] for item in items_data)
        shard = f'order_shard_{user_id % 4}'  # 显式计算分片

        order = Order.objects.using(shard).create(
            user_id=user_id,
            order_no=order_no,
            total_amount=total,
            actual_amount=total,
            remark=remark,
        )

        # 批量创建订单明细(同一分片、同一事务)
        OrderItem.objects.bulk_create([
            OrderItem(
                order_id=order.id,
                product_id=item['product_id'],
                product_name=item['product_name'],
                quantity=item['quantity'],
                unit_price=item['unit_price'],
                total_price=item['unit_price'] * item['quantity'],
            )
            for item in items_data
        ])

        return order

    @staticmethod
    def query_user_orders(user_id: int, page=1, page_size=20):
        """查询用户订单 - 从对应分片读取"""
        shard = f'order_shard_{user_id % 4}'
        queryset = Order.objects.using(shard).filter(
            user_id=user_id
        ).prefetch_related('items').order_by('-created_at')

        offset = (page - 1) * page_size
        total = queryset.count()
        orders = list(queryset[offset:offset + page_size])

        return {
            'total': total,
            'page': page,
            'page_size': page_size,
            'orders': orders,
        }
```

### 3.6 Celery 异步任务

**`src/config/celery.py`**

```python
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('enterprise_platform')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(['tasks'])

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
```

**`src/config/__init__.py`**

```python
from .celery import app as celery_app

__all__ = ('celery_app',)
```

**`src/tasks/order_tasks.py`**

```python
import logging
from celery import shared_task
from apps.order.services import OrderService

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_order_async(self, user_id, items_data, remark=''):
    """异步处理订单 - 如库存扣减、通知等"""
    try:
        order = OrderService.create_order(user_id, items_data, remark)
        logger.info(f'Async order created: {order.order_no}')
        return {'order_id': order.id, 'order_no': order.order_no}
    except Exception as exc:
        logger.error(f'Order creation failed: {exc}')
        raise self.retry(exc=exc)


@shared_task
def sync_order_to_es(order_id):
    """订单同步到 Elasticsearch 用于搜索"""
    # 示例：同步到 ES
    logger.info(f'Syncing order {order_id} to Elasticsearch')
    # es_client.index(index='orders', id=order_id, body={...})
    return True
```

### 3.7 Gunicorn 配置

**`deploy/gunicorn.conf.py`**

```python
import multiprocessing
import os

# 绑定地址
bind = "0.0.0.0:8000"

# Worker 配置
workers = int(os.environ.get('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = 'sync'
worker_connections = 1000
threads = int(os.environ.get('GUNICORN_THREADS', 2))

# 超时
timeout = 30
graceful_timeout = 30
keepalive = 5

# 日志
accesslog = '-'
errorlog = '-'
loglevel = os.environ.get('LOG_LEVEL', 'info')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# 进程标签
proc_name = 'django-enterprise'

# 优雅重启
max_requests = 10000
max_requests_jitter = 1000

# 预加载应用（减少内存占用，但重启较慢）
preload_app = True

# 后台运行
daemon = False
pidfile = '/tmp/gunicorn.pid'
```

---

## 4. MySQL 分库分表方案

### 4.1 分库分表策略

```
                      ┌──────────────────────┐
                      │     应用程序层        │
                      │  OrderShardRouter    │
                      │  user_id % 4 → Shard │
                      └──────────┬───────────┘
                                 │
          ┌──────────────────────┼──────────────────────┐
          │                      │                      │
   ┌──────▼──────┐       ┌──────▼──────┐       ┌──────▼──────┐
   │ MySQL-A     │       │ MySQL-B     │       │ MySQL-C     │
   │ Shard 0     │       │ Shard 1     │       │ Shard 2     │
   │ (user%4=0)  │       │ (user%4=1)  │       │ (user%4=2)  │
   └─────────────┘       └─────────────┘       └─────────────┘
          │
   ┌──────▼──────┐
   │ MySQL-D     │
   │ Shard 3     │
   │ (user%4=3)  │
   └─────────────┘
```

### 4.2 MySQL 主从 + 分片初始化

**`scripts/init_sharding.sql`**

```sql
-- ============================================
-- MySQL 分库分表初始化脚本
-- ============================================

-- 1. 创建默认库（用户/配置）
CREATE DATABASE IF NOT EXISTS enterprise_platform
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

-- 2. 创建四个订单分片库
CREATE DATABASE IF NOT EXISTS enterprise_order_0
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

CREATE DATABASE IF NOT EXISTS enterprise_order_1
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

CREATE DATABASE IF NOT EXISTS enterprise_order_2
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

CREATE DATABASE IF NOT EXISTS enterprise_order_3
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

-- 3. 创建应用用户并授权
CREATE USER IF NOT EXISTS 'django_user'@'%' IDENTIFIED BY 'StrongPassword123!';

GRANT SELECT, INSERT, UPDATE, DELETE ON enterprise_platform.* TO 'django_user'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON enterprise_order_0.* TO 'django_user'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON enterprise_order_1.* TO 'django_user'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON enterprise_order_2.* TO 'django_user'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON enterprise_order_3.* TO 'django_user'@'%';

-- 创只读用户（用于从库）
CREATE USER IF NOT EXISTS 'django_readonly'@'%' IDENTIFIED BY 'ReadOnlyPass456!';
GRANT SELECT ON enterprise_platform.* TO 'django_readonly'@'%';
GRANT SELECT ON enterprise_order_0.* TO 'django_readonly'@'%';
GRANT SELECT ON enterprise_order_1.* TO 'django_readonly'@'%';
GRANT SELECT ON enterprise_order_2.* TO 'django_readonly'@'%';
GRANT SELECT ON enterprise_order_3.* TO 'django_readonly'@'%';

FLUSH PRIVILEGES;

-- 4. 在每个分片库中创建 order_info 表
-- 在 enterprise_order_0 执行:
USE enterprise_order_0;
CREATE TABLE IF NOT EXISTS order_info (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    order_no VARCHAR(32) NOT NULL UNIQUE,
    total_amount DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    discount_amount DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    actual_amount DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    status ENUM('pending','paid','shipped','delivered','cancelled','refunded') NOT NULL DEFAULT 'pending',
    remark TEXT,
    created_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    updated_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at),
    INDEX idx_user_status (user_id, status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS order_item (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    order_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(12,2) NOT NULL,
    INDEX idx_order_id (order_id),
    CONSTRAINT fk_order_item_order FOREIGN KEY (order_id) REFERENCES order_info(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 其他分片库执行相同 DDL（略，可脚本循环执行）
```

### 4.3 批量执行初始化脚本（远程服务器）

**`scripts/migrate.sh`**

```bash
#!/bin/bash
set -euo pipefail

# ============================================
# MySQL 分库分表初始化 - 远程服务器执行版
# 在所有 MySQL 分片服务器上执行 DDL
# ============================================

SHARD_COUNT=4
MYSQL_ROOT_PASS="${MYSQL_ROOT_PASSWORD:-}"

# MySQL 服务器 IP 映射
declare -A SHARD_HOSTS
SHARD_HOSTS[0]="10.0.2.21"   # mysql-shard-0
SHARD_HOSTS[1]="10.0.2.22"   # mysql-shard-1
SHARD_HOSTS[2]="10.0.2.23"   # mysql-shard-2
SHARD_HOSTS[3]="10.0.2.24"   # mysql-shard-3

MASTER_HOST="10.0.2.11"      # mysql-master
SLAVE_HOST="10.0.2.12"       # mysql-slave

echo "=== 1. 初始化主库 ==="
ssh root@${MASTER_HOST} "docker exec mysql-master mysql -u root -p'${MYSQL_ROOT_PASS}'" < scripts/init_sharding.sql

echo "=== 2. 在每个分片服务器上执行 DDL ==="
for i in $(seq 0 $((SHARD_COUNT - 1))); do
    host="${SHARD_HOSTS[$i]}"
    db="enterprise_order_$i"
    echo "Migrating shard $i on host $host, database $db..."

    ssh root@${host} "docker exec mysql-shard mysql -u root -p'${MYSQL_ROOT_PASS}' ${db}" <<SQL
CREATE TABLE IF NOT EXISTS order_info (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    order_no VARCHAR(32) NOT NULL UNIQUE,
    total_amount DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    discount_amount DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    actual_amount DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    status ENUM('pending','paid','shipped','delivered','cancelled','refunded') NOT NULL DEFAULT 'pending',
    remark TEXT,
    created_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    updated_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at),
    INDEX idx_user_status (user_id, status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS order_item (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    order_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(12,2) NOT NULL,
    INDEX idx_order_id (order_id),
    CONSTRAINT fk_order_item_order FOREIGN KEY (order_id) REFERENCES order_info(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
SQL
    echo "Shard $i done."
done

echo "=== 3. 配置主从复制 ==="
# 在 Master 上创建复制用户
ssh root@${MASTER_HOST} "docker exec mysql-master mysql -u root -p'${MYSQL_ROOT_PASS}'" <<SQL
CREATE USER IF NOT EXISTS 'repl_user'@'%' IDENTIFIED BY 'ReplPass456!';
GRANT REPLICATION SLAVE ON *.* TO 'repl_user'@'%';
FLUSH PRIVILEGES;
SQL

# 获取 Master 状态
MASTER_STATUS=$(ssh root@${MASTER_HOST} "docker exec mysql-master mysql -u root -p'${MYSQL_ROOT_PASS}' -e 'SHOW MASTER STATUS\G'")
LOG_FILE=$(echo "$MASTER_STATUS" | grep File | awk '{print $2}')
LOG_POS=$(echo "$MASTER_STATUS" | grep Position | awk '{print $2}')

# 在 Slave 上配置复制
ssh root@${SLAVE_HOST} "docker exec mysql-slave mysql -u root -p'${MYSQL_ROOT_PASS}'" <<SQL
CHANGE MASTER TO
    MASTER_HOST='${MASTER_HOST}',
    MASTER_USER='repl_user',
    MASTER_PASSWORD='ReplPass456!',
    MASTER_LOG_FILE='${LOG_FILE}',
    MASTER_LOG_POS=${LOG_POS};
START SLAVE;
SQL

echo "=== 4. 验证主从状态 ==="
ssh root@${SLAVE_HOST} "docker exec mysql-slave mysql -u root -p'${MYSQL_ROOT_PASS}' -e 'SHOW SLAVE STATUS\G'" \
    | grep -E "Slave_IO_Running|Slave_SQL_Running"

echo "=== All migrations complete ==="
```

---

## 5. Redis 集群部署

### 5.1 Redis 集群架构

```
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  Master 0    │  │  Master 1    │  │  Master 2    │
│  Slots 0-5460│  │Slots 5461-   │  │Slots 10923-  │
│              │  │   10922      │  │   16383      │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │
┌──────▼───────┐  ┌──────▼───────┐  ┌──────▼───────┐
│  Slave 0     │  │  Slave 1     │  │  Slave 2     │
│  (Replica)   │  │  (Replica)   │  │  (Replica)   │
└──────────────┘  └──────────────┘  └──────────────┘

用途分配:
  数据库 0: Celery Broker
  数据库 1: Django Cache
  数据库 2: Session 存储
  数据库 3: 分布式锁
```

### 5.2 使用 Docker 在三台物理服务器上部署 Redis 集群

#### 5.2.1 每台 Redis 服务器初始化

```bash
# ============================================
# 在 redis-node-0 (10.0.3.11)、redis-node-1 (10.0.3.12)、
# redis-node-2 (10.0.3.13) 分别执行
# ============================================

# 创建数据目录
mkdir -p /data/redis /opt/redis/conf

# 创建 Redis 配置文件
cat > /opt/redis/conf/redis.conf <<EOF
port 6379
cluster-enabled yes
cluster-config-file nodes.conf
cluster-node-timeout 5000
cluster-announce-ip <本机IP>        # 修改为实际 IP (如 10.0.3.11)
cluster-announce-port 6379
cluster-announce-bus-port 16379
appendonly yes
appendfsync everysec
maxmemory 4gb
maxmemory-policy allkeys-lru
protected-mode no
bind 0.0.0.0
requirepass RedisPass789!
masterauth RedisPass789!
save 900 1
save 300 10
save 60 10000
dir /data/redis
EOF

# 注意修改 cluster-announce-ip 为本机实际 IP
```

#### 5.2.2 启动 Redis 容器

```bash
# 每台 Redis 服务器执行同样的 docker run 命令
# redis-node-0:
docker run -d --name redis-cluster --restart=always \
    --network host \
    -v /data/redis:/data \
    -v /opt/redis/conf/redis.conf:/usr/local/etc/redis/redis.conf \
    redis:7.0-alpine \
    redis-server /usr/local/etc/redis/redis.conf

# redis-node-1 和 redis-node-2 同样操作
```

#### 5.2.3 创建集群

```bash
# 在任意一台 Redis 服务器上执行
docker exec redis-cluster redis-cli -a RedisPass789! --cluster create \
    10.0.3.11:6379 \
    10.0.3.12:6379 \
    10.0.3.13:6379 \
    --cluster-replicas 0

# 验证集群状态
docker exec redis-cluster redis-cli -a RedisPass789! cluster info
# 期望输出:
# cluster_state:ok
# cluster_slots_assigned:16384
# cluster_slots_ok:16384
# cluster_known_nodes:3

docker exec redis-cluster redis-cli -a RedisPass789! cluster nodes
```

### 5.3 初始化 Redis 集群（无容器方案，直接安装）

如果不想用 Docker，在三台 Redis 服务器上直接安装：

```bash
# 每台服务器执行
add-apt-repository -y ppa:redislabs/redis
apt update && apt install -y redis-server redis-tools

# 修改 /etc/redis/redis.conf
# cluster-enabled yes
# cluster-config-file nodes.conf
# cluster-node-timeout 5000
# appendonly yes
# bind 0.0.0.0
# requirepass RedisPass789!
# masterauth RedisPass789!

systemctl enable redis-server --now

# 创建集群（任意一台）
redis-cli -a RedisPass789! --cluster create \
    10.0.3.11:6379 \
    10.0.3.12:6379 \
    10.0.3.13:6379 \
    --cluster-replicas 0
```

### 5.4 Python Redis 客户端封装

**`src/utils/redis_client.py`**

```python
"""
Redis 集群客户端封装
支持: 缓存、分布式锁、计数器
"""
import redis
from functools import wraps
import hashlib
import json


class RedisClusterClient:
    """Redis 集群客户端"""

    def __init__(self, startup_nodes, password=None, max_connections=50):
        self.client = redis.RedisCluster(
            startup_nodes=startup_nodes,
            password=password,
            decode_responses=True,
            max_connections=max_connections,
            skip_full_coverage_check=True,
        )

    # ---- 缓存 API ----
    def cache_get(self, key):
        """获取缓存"""
        return self.client.get(key)

    def cache_set(self, key, value, ttl=300):
        """设置缓存，默认 5 分钟"""
        self.client.setex(key, ttl, value)

    def cache_get_or_set(self, key, factory, ttl=300):
        """缓存穿透保护: 获取或设置缓存"""
        value = self.client.get(key)
        if value is not None:
            return json.loads(value)
        value = factory()
        self.client.setex(key, ttl, json.dumps(value, ensure_ascii=False))
        return value

    def cache_delete(self, key):
        self.client.delete(key)

    def cache_delete_pattern(self, pattern):
        """批量删除匹配模式的所有 key"""
        cursor = 0
        while True:
            cursor, keys = self.client.scan(cursor=cursor, match=pattern, count=100)
            if keys:
                self.client.delete(*keys)
            if cursor == 0:
                break

    # ---- 分布式锁 ----
    def acquire_lock(self, lock_name, ttl=10):
        """
        获取分布式锁
        返回 lock_id 用于释放
        """
        lock_id = hashlib.md5(str(hash(lock_name)).encode()).hexdigest()[:16]
        acquired = self.client.set(
            f'lock:{lock_name}',
            lock_id,
            nx=True,
            ex=ttl,
        )
        return lock_id if acquired else None

    def release_lock(self, lock_name, lock_id):
        """释放分布式锁（Lua 脚本保证原子性）"""
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        self.client.eval(lua_script, 1, f'lock:{lock_name}', lock_id)

    # ---- 计数器 ----
    def increment(self, key, amount=1, ttl=None):
        """原子递增"""
        result = self.client.incrby(key, amount)
        if ttl:
            self.client.expire(key, ttl)
        return result

    # ---- 排行榜 ----
    def zadd(self, key, mapping):
        self.client.zadd(key, mapping)

    def zrange(self, key, start, end, desc=True):
        return self.client.zrange(key, start, end, desc=desc, withscores=True)


# 单例
_redis_instance = None


def get_redis_client():
    global _redis_instance
    if _redis_instance is None:
        from django.conf import settings
        startup_nodes = [
            {"host": "redis-node-0", "port": 6379},
            {"host": "redis-node-1", "port": 6379},
            {"host": "redis-node-2", "port": 6379},
        ]
        _redis_instance = RedisClusterClient(
            startup_nodes=startup_nodes,
            password=getattr(settings, 'REDIS_PASSWORD', None),
        )
    return _redis_instance
```

---

## 6. Nginx 反向代理与负载均衡

### 6.1 Nginx 配置（反向代理 + 静态资源）

**`deploy/nginx/nginx.conf`**

```nginx
user nginx;
worker_processes auto;
worker_rlimit_nofile 65535;

error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 4096;
    use epoll;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # 日志格式 - JSON 格式方便 ELK 采集
    log_format json_combined escape=json '{'
        '"time":"$time_iso8601",'
        '"remote_addr":"$remote_addr",'
        '"x_forwarded_for":"$http_x_forwarded_for",'
        '"request_method":"$request_method",'
        '"request_uri":"$request_uri",'
        '"status":$status,'
        '"body_bytes_sent":$body_bytes_sent,'
        '"request_time":$request_time,'
        '"upstream_response_time":"$upstream_response_time",'
        '"upstream_addr":"$upstream_addr",'
        '"http_referer":"$http_referer",'
        '"http_user_agent":"$http_user_agent",'
        '"trace_id":"$http_x_trace_id"'
    '}';

    access_log /var/log/nginx/access.log json_combined;

    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    # Gzip 压缩
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_min_length 1000;
    gzip_types text/plain text/css text/xml text/javascript
               application/json application/javascript application/xml+rss
               application/rss+xml font/truetype font/opentype
               application/vnd.ms-fontobject image/svg+xml;

    # 限流
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_conn_zone $binary_remote_addr zone=conn_limit:10m;

    # 上游 - Django 应用服务器
    upstream django_backend {
        least_conn;  # 最少连接调度算法
        server django-app-0:8000 weight=5 max_fails=3 fail_timeout=30s;
        server django-app-1:8000 weight=5 max_fails=3 fail_timeout=30s;
        server django-app-2:8000 weight=3 max_fails=3 fail_timeout=30s;
        keepalive 32;
    }

    server {
        listen 80;
        server_name api.example.com;

        # 重定向到 HTTPS（生产环境）
        return 301 https://$host$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name api.example.com;

        # SSL 证书
        ssl_certificate /etc/nginx/certs/fullchain.pem;
        ssl_certificate_key /etc/nginx/certs/privkey.pem;
        ssl_session_timeout 1d;
        ssl_session_cache shared:MozSSL:10m;
        ssl_session_tickets off;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;

        # 安全头
        add_header X-Frame-Options "DENY" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Strict-Transport-Security "max-age=63072000" always;

        # 客户端上传大小限制
        client_max_body_size 50m;
        client_body_buffer_size 128k;

        # 静态资源
        location /static/ {
            alias /app/staticfiles/;
            expires 30d;
            add_header Cache-Control "public, immutable";
        }

        location /media/ {
            alias /app/media/;
            expires 7d;
            add_header Cache-Control "public";
        }

        # 健康检查
        location /health/ {
            access_log off;
            return 200 '{"status": "ok"}';
            add_header Content-Type application/json;
        }

        # API 请求
        location /api/ {
            limit_req zone=api_limit burst=20 nodelay;
            limit_conn conn_limit 10;

            proxy_pass http://django_backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header X-Trace-ID $request_id;

            # 超时
            proxy_connect_timeout 10s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;

            # 缓冲
            proxy_buffering on;
            proxy_buffer_size 4k;
            proxy_buffers 8 16k;
            proxy_busy_buffers_size 32k;
        }

        # Admin
        location /admin/ {
            limit_req zone=api_limit burst=5 nodelay;
            proxy_pass http://django_backend;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

---

## 7. Docker 容器化

### 7.1 Django Dockerfile

**`deploy/docker/Dockerfile`**

```dockerfile
# ============================
# Stage 1: 构建依赖
# ============================
FROM python:3.11-slim-bookworm AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 安装依赖
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# ============================
# Stage 2: 运行环境
# ============================
FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_ENV=production \
    PATH="/home/django/.local/bin:$PATH"

# 创建非 root 用户
RUN groupadd -r django && useradd -r -g django django \
    && mkdir -p /app /app/staticfiles /app/media /app/logs \
    && chown -R django:django /app

# 安装运行时依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmariadb-dev-compat \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 从 builder 复制 Python 包
COPY --from=builder /root/.local /home/django/.local

# 复制应用代码
COPY --chown=django:django src/ /app/
COPY --chown=django:django deploy/gunicorn.conf.py /app/

WORKDIR /app
USER django

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

EXPOSE 8000

# 启动命令
CMD ["gunicorn", "config.wsgi:application", "-c", "gunicorn.conf.py"]
```

**`requirements.txt`**

```
Django==4.2.11
djangorestframework==3.14.0
django-cors-headers==4.3.1
whitenoise==6.6.0
djangorestframework-simplejwt==5.3.1
django-redis==5.4.0
django-celery-results==2.5.1
mysqlclient==2.2.4
celery==5.3.6
redis==5.0.1
gunicorn==21.2.0
gevent==23.9.1
sentry-sdk==1.39.1
uWSGI==2.0.23
```

### 7.2 服务器端 Docker Compose（用于非 K8s 环境的服务）

以下 docker-compose.yml 用于直接在服务器上编排 MySQL 分片、Redis、Nginx 等基础服务（当这些服务不走 K8s 时使用）。

> **注意**: 在实际企业架构中，MySQL/Redis 通常独立部署在物理机或 K8s StatefulSet 上，这里提供 Docker Compose 方案作为备选——适合中小规模或非 K8s 环境。

**`deploy/docker/docker-compose.yml`**（仅部署在对应物理服务器上）

```yaml
version: '3.8'

services:
  # ---- MySQL Master (默认库，部署在 mysql-master 服务器 10.0.2.11) ----
  mysql-master:
    image: mysql:8.0
    container_name: mysql-master
    restart: unless-stopped
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: enterprise_platform
    ports:
      - "3306:3306"
    volumes:
      - /data/mysql-master:/var/lib/mysql
      - ../../scripts/init_sharding.sql:/docker-entrypoint-initdb.d/init.sql
    command: >
      --server-id=1
      --log-bin=mysql-bin
      --binlog-format=ROW
      --character-set-server=utf8mb4
      --collation-server=utf8mb4_unicode_ci
      --default-authentication-plugin=mysql_native_password
      --max_connections=1000
      --innodb-buffer-pool-size=16G
      --innodb-log-file-size=2G
      --innodb-flush-log-at-trx-commit=2
      --innodb-flush-method=O_DIRECT
      --innodb-io-capacity=2000
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5
    network_mode: host    # 使用宿主机网络，避免 Docker 网络开销

  # ---- MySQL Slave (只读，部署在 mysql-slave 服务器 10.0.2.12) ----
  mysql-slave:
    image: mysql:8.0
    container_name: mysql-slave
    restart: unless-stopped
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
    ports:
      - "3306:3306"
    volumes:
      - /data/mysql-slave:/var/lib/mysql
    command: >
      --server-id=2
      --character-set-server=utf8mb4
      --collation-server=utf8mb4_unicode_ci
      --max_connections=500
      --read-only=1
    network_mode: host

  # ---- MySQL 分片节点 (各部署在 mysql-shard-0~3 服务器) ----
  # 以 shard-0 为例，shard-1/2/3 同理修改 server-id 和数据库名
  mysql-shard-0:
    image: mysql:8.0
    container_name: mysql-shard-0
    restart: unless-stopped
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: enterprise_order_0
    ports:
      - "3306:3306"
    volumes:
      - /data/mysql-shard-0:/var/lib/mysql
    command: >
      --server-id=10
      --character-set-server=utf8mb4
      --innodb-buffer-pool-size=8G
      --max_connections=500
    network_mode: host
```

### 7.3 构建镜像并推送到 Harbor 私有仓库

```bash
# ============================================
# 在开发机或 Jenkins 服务器上执行
# ============================================

# 1. 构建镜像（多阶段构建，产物小）
docker build \
    -t harbor-registry:8443/enterprise-platform/django:latest \
    -t harbor-registry:8443/enterprise-platform/django:v1.0.0 \
    -f deploy/docker/Dockerfile .

# 2. 登录 Harbor
docker login harbor-registry:8443 -u admin -p Harbor12345

# 3. 推送镜像
docker push harbor-registry:8443/enterprise-platform/django:latest
docker push harbor-registry:8443/enterprise-platform/django:v1.0.0

# 4. 验证镜像
docker pull harbor-registry:8443/enterprise-platform/django:latest

# 5. 本地测试运行
docker run --rm -p 8000:8000 \
    -e DJANGO_ENV=production \
    -e DB_HOST=mysql-master \
    --add-host mysql-master:10.0.2.11 \
    harbor-registry:8443/enterprise-platform/django:latest
```

---

## 8. Kubernetes 部署

### 8.1 命名空间与基础资源

**`deploy/k8s/namespace.yaml`**

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: enterprise-platform
  labels:
    name: enterprise-platform
    environment: production
```

**`deploy/k8s/configmap.yaml`**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: django-config
  namespace: enterprise-platform
data:
  DJANGO_ENV: "production"
  LOG_LEVEL: "INFO"
  ALLOWED_HOSTS: "api.example.com,localhost"
  CORS_ORIGINS: "https://admin.example.com,https://www.example.com"
  DB_HOST: "mysql-master-service"
  DB_READ_HOST: "mysql-slave-service"
  DB_PORT: "3306"
  DB_NAME: "enterprise_platform"
  DB_SHARD0_HOST: "mysql-shard-0-service"
  DB_SHARD1_HOST: "mysql-shard-1-service"
  DB_SHARD2_HOST: "mysql-shard-2-service"
  DB_SHARD3_HOST: "mysql-shard-3-service"
  CELERY_BROKER_URL: "redis://redis-cluster-service:6379/0"
  GUNICORN_WORKERS: "4"
  GUNICORN_THREADS: "2"
```

**`deploy/k8s/secret.yaml`**

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: django-secrets
  namespace: enterprise-platform
type: Opaque
stringData:
  DJANGO_SECRET_KEY: "your-production-secret-key-change-this"
  DB_USER: "django_user"
  DB_PASSWORD: "StrongPassword123!"
  REDIS_PASSWORD: "redis-password-here"
  SENTRY_DSN: "https://xxx@sentry.io/xxx"
```

### 8.2 Django Deployment

**`deploy/k8s/django-deployment.yaml`**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: django-app
  namespace: enterprise-platform
  labels:
    app: django-app
    version: v1
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0  # 零停机更新
  selector:
    matchLabels:
      app: django-app
  template:
    metadata:
      labels:
        app: django-app
        version: v1
    spec:
      terminationGracePeriodSeconds: 30
      affinity:
        podAntiAffinity:  # Pod 反亲和 - 分散到不同节点
          preferredDuringSchedulingIgnoredDuringExecution:
            - weight: 100
              podAffinityTerm:
                labelSelector:
                  matchLabels:
                    app: django-app
                topologyKey: kubernetes.io/hostname
      containers:
        - name: django
          image: harbor-registry:8443/enterprise-platform/django:latest
          imagePullPolicy: Always
          ports:
            - containerPort: 8000
              protocol: TCP
          envFrom:
            - configMapRef:
                name: django-config
            - secretRef:
                name: django-secrets
          resources:
            requests:
              cpu: "500m"
              memory: "512Mi"
            limits:
              cpu: "2"
              memory: "2Gi"
          livenessProbe:
            httpGet:
              path: /health/
              port: 8000
            initialDelaySeconds: 30
            periodSeconds: 10
            timeoutSeconds: 5
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /health/
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 5
            timeoutSeconds: 3
            failureThreshold: 2
          lifecycle:
            preStop:
              exec:
                command: ["/bin/sh", "-c", "sleep 10"]  # 等待连接排空
          volumeMounts:
            - name: static-files
              mountPath: /app/staticfiles
            - name: logs
              mountPath: /app/logs
      volumes:
        - name: static-files
          persistentVolumeClaim:
            claimName: django-static-pvc
        - name: logs
          emptyDir: {}
      initContainers:
        - name: django-migrate
          image: harbor-registry:8443/enterprise-platform/django:latest
          # 仅迁移 default 数据库（Django 内置表）。
          # 订单分片库的 DDL 由 scripts/migrate.sh 独立执行（见 4.3 节）。
          command: ["python", "manage.py", "migrate", "--noinput", "--database=default"]
          envFrom:
            - configMapRef:
                name: django-config
            - secretRef:
                name: django-secrets
        - name: collect-static
          image: harbor-registry:8443/enterprise-platform/django:latest
          command: ["python", "manage.py", "collectstatic", "--noinput"]
          volumeMounts:
            - name: static-files
              mountPath: /app/staticfiles
```

**`deploy/k8s/django-service.yaml`**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: django-service
  namespace: enterprise-platform
  labels:
    app: django-app
spec:
  type: ClusterIP
  selector:
    app: django-app
  ports:
    - name: http
      port: 8000
      targetPort: 8000
      protocol: TCP
  sessionAffinity: None
```

**`deploy/k8s/django-hpa.yaml`**

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: django-hpa
  namespace: enterprise-platform
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: django-app
  minReplicas: 3
  maxReplicas: 20
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300  # 5 分钟窗口
      policies:
        - type: Pods
          value: 1
          periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
        - type: Percent
          value: 100
          periodSeconds: 30
```

**金丝雀 Deployment（Jenkinsfile Canary Deploy 阶段引用）**

**`deploy/k8s/django-canary-deployment.yaml`**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: django-canary
  namespace: enterprise-platform
  labels:
    app: django-canary
spec:
  replicas: 1
  selector:
    matchLabels:
      app: django-canary
  template:
    metadata:
      labels:
        app: django-canary
    spec:
      imagePullSecrets:
        - name: harbor-registry-secret
      containers:
        - name: django
          image: harbor-registry:8443/enterprise-platform/django:canary
          ports:
            - containerPort: 8000
          envFrom:
            - configMapRef:
                name: django-config
            - secretRef:
                name: django-secrets
          resources:
            requests:
              cpu: "250m"
              memory: "256Mi"
            limits:
              cpu: "1"
              memory: "1Gi"
---
apiVersion: v1
kind: Service
metadata:
  name: django-canary-service
  namespace: enterprise-platform
spec:
  selector:
    app: django-canary
  ports:
    - port: 8000
      targetPort: 8000
```

### 8.3 Celery Worker Deployment

**`deploy/k8s/celery-deployment.yaml`**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: celery-worker
  namespace: enterprise-platform
  labels:
    app: celery-worker
spec:
  replicas: 4
  selector:
    matchLabels:
      app: celery-worker
  template:
    metadata:
      labels:
        app: celery-worker
    spec:
      containers:
        - name: celery-worker
          image: harbor-registry:8443/enterprise-platform/django:latest
          command: ["celery", "-A", "config", "worker", "-l", "info", "-c", "4"]
          envFrom:
            - configMapRef:
                name: django-config
            - secretRef:
                name: django-secrets
          resources:
            requests:
              cpu: "500m"
              memory: "512Mi"
            limits:
              cpu: "2"
              memory: "2Gi"
```

**Celery Beat 定时任务调度器**

**`deploy/k8s/celery-beat-deployment.yaml`**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: celery-beat
  namespace: enterprise-platform
  labels:
    app: celery-beat
spec:
  replicas: 1       # Beat 必须单实例，否则重复执行
  strategy:
    type: Recreate  # 先停后启，避免两个 Beat 同时运行
  selector:
    matchLabels:
      app: celery-beat
  template:
    metadata:
      labels:
        app: celery-beat
    spec:
      containers:
        - name: celery-beat
          image: harbor-registry:8443/enterprise-platform/django:latest
          command: ["celery", "-A", "config", "beat", "-l", "info"]
          envFrom:
            - configMapRef:
                name: django-config
            - secretRef:
                name: django-secrets
          resources:
            requests:
              cpu: "100m"
              memory: "256Mi"
            limits:
              cpu: "500m"
              memory: "512Mi"
```

### 8.4 Redis StatefulSet

**`deploy/k8s/redis-statefulset.yaml`**

```yaml
---
# Service for Redis nodes inter-communication
apiVersion: v1
kind: Service
metadata:
  name: redis-cluster-service
  namespace: enterprise-platform
spec:
  clusterIP: None
  selector:
    app: redis-cluster
  ports:
    - name: client
      port: 6379
      targetPort: 6379
    - name: gossip
      port: 16379
      targetPort: 16379
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: redis-cluster
  namespace: enterprise-platform
spec:
  serviceName: redis-cluster-service
  replicas: 6    # 3 Master + 3 Slave
  selector:
    matchLabels:
      app: redis-cluster
  template:
    metadata:
      labels:
        app: redis-cluster
    spec:
      containers:
        - name: redis
          image: redis:7.0-alpine
          ports:
            - containerPort: 6379
              name: client
            - containerPort: 16379
              name: gossip
          command:
            - redis-server
          args:
            - /usr/local/etc/redis/redis.conf
          env:
            - name: REDIS_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: django-secrets
                  key: REDIS_PASSWORD
          resources:
            requests:
              cpu: "500m"
              memory: "1Gi"
            limits:
              cpu: "2"
              memory: "4Gi"
          volumeMounts:
            - name: redis-config
              mountPath: /etc/redis
            - name: redis-data
              mountPath: /data
          livenessProbe:
            tcpSocket:
              port: 6379
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            exec:
              command:
                - redis-cli
                - -a
                - "$(REDIS_PASSWORD)"
                - ping
            initialDelaySeconds: 10
            periodSeconds: 5
      # initContainer: 在 Pod 启动时动态生成 redis.conf（Pod IP 在 ConfigMap 中无法预知）
      initContainers:
        - name: generate-redis-config
          image: busybox:1.36
          command:
            - sh
            - -c
            - |
              POD_IP=\$(hostname -i)
              cat > /etc/redis/redis.conf << CONFEOF
              port 6379
              cluster-enabled yes
              cluster-config-file nodes.conf
              cluster-node-timeout 5000
              cluster-announce-ip \${POD_IP}
              cluster-announce-port 6379
              cluster-announce-bus-port 16379
              appendonly yes
              appendfsync everysec
              maxmemory 2gb
              maxmemory-policy allkeys-lru
              protected-mode no
              bind 0.0.0.0
              requirepass \${REDIS_PASSWORD}
              masterauth \${REDIS_PASSWORD}
              save 900 1
              save 300 10
              save 60 10000
              CONFEOF
              echo "Generated redis.conf with announce-ip=\${POD_IP}"
          env:
            - name: REDIS_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: django-secrets
                  key: REDIS_PASSWORD
          volumeMounts:
            - name: redis-config
              mountPath: /etc/redis
      volumes:
        - name: redis-config
          emptyDir: {}
  volumeClaimTemplates:
    - metadata:
        name: redis-data
      spec:
        accessModes: ["ReadWriteOnce"]
        storageClassName: "ssd-storage"
        resources:
          requests:
            storage: 20Gi
```

**初始化 Redis 集群（StatefulSet 启动后执行）**

```bash
# Pod 全部启动后，手动创建集群
# 先获取所有 Redis Pod 的 IP
REDIS_PODS=$(kubectl get pods -l app=redis-cluster -n enterprise-platform \
    -o jsonpath='{range.items[*]}{.status.podIP}:6379 {end}')

kubectl exec redis-cluster-0 -n enterprise-platform -- \
    redis-cli -a "$REDIS_PASSWORD" --cluster create $REDIS_PODS --cluster-replicas 1 --cluster-yes

# 验证
kubectl exec -it redis-cluster-0 -n enterprise-platform -- redis-cli -a "$REDIS_PASSWORD" cluster info
```

**Redis Metrics Service（Prometheus 采集端点）**

```yaml
---
apiVersion: v1
kind: Service
metadata:
  name: redis-metrics-service
  namespace: enterprise-platform
  labels:
    app: redis-cluster
spec:
  clusterIP: None
  selector:
    app: redis-cluster
  ports:
    - name: metrics
      port: 9121
      targetPort: 6379
```

### 8.5 MySQL 全套 StatefulSet

#### 8.5.1 MySQL Secret

**`deploy/k8s/mysql-secret.yaml`**

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: mysql-secrets
  namespace: enterprise-platform
type: Opaque
stringData:
  root-password: "MySQLRootPass999!"
  replication-user: "repl_user"
  replication-password: "ReplPass456!"
```

#### 8.5.2 MySQL Master（默认库）

**`deploy/k8s/mysql-master-svc.yaml`**

```yaml
---
apiVersion: v1
kind: Service
metadata:
  name: mysql-master-service
  namespace: enterprise-platform
  labels:
    app: mysql-master
spec:
  clusterIP: None
  selector:
    app: mysql-master
  ports:
    - port: 3306
      targetPort: 3306
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mysql-master
  namespace: enterprise-platform
spec:
  serviceName: mysql-master-service
  replicas: 1
  selector:
    matchLabels:
      app: mysql-master
  template:
    metadata:
      labels:
        app: mysql-master
    spec:
      containers:
        - name: mysql
          image: mysql:8.0
          ports:
            - containerPort: 3306
          env:
            - name: MYSQL_ROOT_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: mysql-secrets
                  key: root-password
            - name: MYSQL_DATABASE
              value: "enterprise_platform"
          args:
            - --server-id=1
            - --log-bin=mysql-bin
            - --binlog-format=ROW
            - --character-set-server=utf8mb4
            - --collation-server=utf8mb4_unicode_ci
            - --max-connections=1000
            - --innodb-buffer-pool-size=4G
            - --innodb-flush-log-at-trx-commit=2
          resources:
            requests:
              cpu: "2"
              memory: "4Gi"
            limits:
              cpu: "4"
              memory: "16Gi"
          volumeMounts:
            - name: mysql-data
              mountPath: /var/lib/mysql
          livenessProbe:
            exec:
              command: ["mysqladmin", "ping", "-h", "localhost"]
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            exec:
              command: ["mysql", "-h", "localhost", "-e", "SELECT 1"]
            initialDelaySeconds: 10
            periodSeconds: 5
  volumeClaimTemplates:
    - metadata:
        name: mysql-data
      spec:
        accessModes: ["ReadWriteOnce"]
        storageClassName: "ssd-storage"
        resources:
          requests:
            storage: 200Gi
```

#### 8.5.3 MySQL Slave（只读）

```yaml
---
apiVersion: v1
kind: Service
metadata:
  name: mysql-slave-service
  namespace: enterprise-platform
spec:
  clusterIP: None
  selector:
    app: mysql-slave
  ports:
    - port: 3306
      targetPort: 3306
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mysql-slave
  namespace: enterprise-platform
spec:
  serviceName: mysql-slave-service
  replicas: 1
  selector:
    matchLabels:
      app: mysql-slave
  template:
    metadata:
      labels:
        app: mysql-slave
    spec:
      containers:
        - name: mysql
          image: mysql:8.0
          ports:
            - containerPort: 3306
          env:
            - name: MYSQL_ROOT_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: mysql-secrets
                  key: root-password
          args:
            - --server-id=2
            - --character-set-server=utf8mb4
            - --collation-server=utf8mb4_unicode_ci
            - --max-connections=500
            - --read-only=1
          resources:
            requests:
              cpu: "1"
              memory: "2Gi"
            limits:
              cpu: "2"
              memory: "8Gi"
          volumeMounts:
            - name: mysql-data
              mountPath: /var/lib/mysql
  volumeClaimTemplates:
    - metadata:
        name: mysql-data
      spec:
        accessModes: ["ReadWriteOnce"]
        storageClassName: "ssd-storage"
        resources:
          requests:
            storage: 200Gi
```

#### 8.5.4 自动配置主从复制（K8s Job）

MySQL Slave Pod 启动后，此 Job 自动配置主从关系：

**`deploy/k8s/mysql-replication-setup-job.yaml`**

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: mysql-replication-setup
  namespace: enterprise-platform
spec:
  ttlSecondsAfterFinished: 300    # 完成后 5 分钟自动清理
  template:
    spec:
      restartPolicy: OnFailure
      containers:
        - name: setup-replication
          image: mysql:8.0
          command:
            - bash
            - -c
            - |
              set -e
              echo "=== 1. 在 Master 上创建复制用户 ==="
              mysql -h mysql-master-service -u root -p"$MYSQL_ROOT_PASSWORD" -e "
                CREATE USER IF NOT EXISTS 'repl_user'@'%' IDENTIFIED BY '$REPL_PASSWORD';
                GRANT REPLICATION SLAVE ON *.* TO 'repl_user'@'%';
                FLUSH PRIVILEGES;
              "

              echo "=== 2. 获取 Master 状态 ==="
              MASTER_STATUS=$(mysql -h mysql-master-service -u root -p"$MYSQL_ROOT_PASSWORD" \
                  -e "SHOW MASTER STATUS\G" -s --skip-column-names)
              LOG_FILE=$(echo "$MASTER_STATUS" | awk '/File:/{print $2}')
              LOG_POS=$(echo "$MASTER_STATUS" | awk '/Position:/{print $2}')
              echo "Master: ${LOG_FILE}:${LOG_POS}"

              echo "=== 3. 在 Slave 上配置复制 ==="
              mysql -h mysql-slave-service -u root -p"$MYSQL_ROOT_PASSWORD" -e "
                STOP SLAVE;
                CHANGE MASTER TO
                  MASTER_HOST='mysql-master-service',
                  MASTER_PORT=3306,
                  MASTER_USER='repl_user',
                  MASTER_PASSWORD='$REPL_PASSWORD',
                  MASTER_LOG_FILE='${LOG_FILE}',
                  MASTER_LOG_POS=${LOG_POS};
                START SLAVE;
              "

              echo "=== 4. 验证 Slave 状态 ==="
              sleep 3
              mysql -h mysql-slave-service -u root -p"$MYSQL_ROOT_PASSWORD" \
                  -e "SHOW SLAVE STATUS\G" | grep -E "Slave_IO_Running|Slave_SQL_Running"

              echo "=== MySQL replication setup complete ==="
          env:
            - name: MYSQL_ROOT_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: mysql-secrets
                  key: root-password
            - name: REPL_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: mysql-secrets
                  key: replication-password
```

部署后执行：

```bash
# 在 MySQL Master 和 Slave StatefulSet 首次 Ready 后
kubectl apply -f deploy/k8s/mysql-replication-setup-job.yaml

# 查看 Job 状态
kubectl logs -f job/mysql-replication-setup -n enterprise-platform
kubectl get job -n enterprise-platform
```

#### 8.5.5 MySQL 分片 0~3（模板，复制修改即可）

**`deploy/k8s/mysql-shard-statefulset.yaml`** — 以 shard-0 为例，shard-1/2/3 需修改以下字段：

| 分片 | `name` | `app` label | `server-id` | `MYSQL_DATABASE` |
|------|--------|-------------|-------------|-------------------|
| shard-0 | mysql-shard-0 | mysql-shard-0 | 10 | enterprise_order_0 |
| shard-1 | mysql-shard-1 | mysql-shard-1 | 11 | enterprise_order_1 |
| shard-2 | mysql-shard-2 | mysql-shard-2 | 12 | enterprise_order_2 |
| shard-3 | mysql-shard-3 | mysql-shard-3 | 13 | enterprise_order_3 |

```yaml
# 示例: mysql-shard-0 (其他 shard 按上表修改对应字段即可)
---
apiVersion: v1
kind: Service
metadata:
  name: mysql-shard-0-service
  namespace: enterprise-platform
  labels:
    app: mysql-shard-0
spec:
  clusterIP: None
  selector:
    app: mysql-shard-0
  ports:
    - port: 3306
      targetPort: 3306
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mysql-shard-0
  namespace: enterprise-platform
spec:
  serviceName: mysql-shard-0-service
  replicas: 1
  selector:
    matchLabels:
      app: mysql-shard-0
  template:
    metadata:
      labels:
        app: mysql-shard-0
    spec:
      containers:
        - name: mysql
          image: mysql:8.0
          ports:
            - containerPort: 3306
          env:
            - name: MYSQL_ROOT_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: mysql-secrets
                  key: root-password
            - name: MYSQL_DATABASE
              value: "enterprise_order_0"
          args:
            - --server-id=10
            - --character-set-server=utf8mb4
            - --collation-server=utf8mb4_unicode_ci
            - --max-connections=500
            - --innodb-buffer-pool-size=4G
          resources:
            requests:
              cpu: "1000m"
              memory: "2Gi"
            limits:
              cpu: "4"
              memory: "8Gi"
          volumeMounts:
            - name: mysql-data
              mountPath: /var/lib/mysql
          livenessProbe:
            exec:
              command: ["mysqladmin", "ping", "-h", "localhost"]
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            exec:
              command: ["mysql", "-h", "localhost", "-e", "SELECT 1"]
            initialDelaySeconds: 10
            periodSeconds: 5
  volumeClaimTemplates:
    - metadata:
        name: mysql-data
      spec:
        accessModes: ["ReadWriteOnce"]
        storageClassName: "ssd-storage"
        resources:
          requests:
            storage: 100Gi
```

### 8.6 存储类与持久化存储

#### 8.6.1 创建 local-path StorageClass（SSD 本地卷，用于数据库）

> **原因**: MySQL/Redis StatefulSet 引用的 `ssd-storage` 必须预先创建，否则 PVC 永远 Pending。使用 Rancher local-path-provisioner 自动创建基于 hostPath 的 PV，适合裸金属服务器。

```bash
# 在 K8s Master 执行
kubectl apply -f https://raw.githubusercontent.com/rancher/local-path-provisioner/v0.0.26/deploy/local-path-storage.yaml

# 重命名为 ssd-storage（与 StatefulSet 中的 storageClassName 匹配）
kubectl patch storageclass local-path -p '{"metadata": {"name": "ssd-storage"}}'
# 注意：local-path 是默认名，patch 后删除旧的
kubectl delete storageclass local-path --ignore-not-found

# 验证
kubectl get storageclass
# NAME           PROVISIONER                    RECLAIMPOLICY   VOLUMEBINDINGMODE
# nfs-storage    nfs.csi.k8s.io                Retain          Immediate
# ssd-storage    rancher.io/local-path          Delete          WaitForFirstConsumer
```

> **说明**: `local-path-provisioner` 在 Pod 所在节点上自动创建 `hostPath` 目录（默认 `/opt/local-path-provisioner`）并绑定 PV。数据在节点本地磁盘上，IO 性能接近裸盘，适合数据库。缺点是 Pod 和 PV 绑定在同一个节点，节点故障时数据丢失——生产环境应配合定期备份。

#### 8.6.2 PVC 定义

**`deploy/k8s/pvc.yaml`**

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: django-static-pvc
  namespace: enterprise-platform
spec:
  accessModes:
    - ReadWriteMany  # 多个 Pod 共享静态文件
  resources:
    requests:
      storage: 10Gi
  storageClassName: nfs-storage
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: redis-data-pvc
  namespace: enterprise-platform
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi
  storageClassName: ssd-storage
```

### 8.7 Ingress（外部入口）

**`deploy/k8s/ingress.yaml`**

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: enterprise-ingress
  namespace: enterprise-platform
  annotations:
    nginx.ingress.kubernetes.io/proxy-body-size: "50m"
    nginx.ingress.kubernetes.io/proxy-connect-timeout: "10"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "60"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/configuration-snippet: |
      more_set_headers "X-Frame-Options: DENY";
      more_set_headers "X-Content-Type-Options: nosniff";
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - api.example.com
      secretName: api-tls-cert
  rules:
    - host: api.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: django-service
                port:
                  number: 8000
```

### 8.8 创建 Harbor 镜像拉取 Secret + 一键部署

```bash
#!/bin/bash
# deploy/k8s/deploy-all.sh
set -euo pipefail

NAMESPACE="enterprise-platform"
REGISTRY="harbor-registry:8443"

echo "=== 1. 创建命名空间 ==="
kubectl apply -f deploy/k8s/namespace.yaml

echo "=== 2. 创建 Secret 和 ConfigMap ==="
kubectl apply -f deploy/k8s/secret.yaml
kubectl apply -f deploy/k8s/configmap.yaml

echo "=== 3. 创建 Harbor 镜像拉取 Secret ==="
kubectl create secret docker-registry harbor-registry-secret \
    --docker-server=harbor-registry:8443 \
    --docker-username=admin \
    --docker-password=Harbor12345 \
    --docker-email=admin@example.com \
    -n $NAMESPACE \
    --dry-run=client -o yaml | kubectl apply -f -

echo "=== 4. 创建 PVC ==="
kubectl apply -f deploy/k8s/pvc.yaml

echo "=== 5. 部署 MySQL ==="
kubectl apply -f deploy/k8s/mysql-secret.yaml
kubectl apply -f deploy/k8s/mysql-master-svc.yaml
kubectl apply -f deploy/k8s/mysql-slave-svc.yaml
for i in 0 1 2 3; do
    # 每个分片需要单独 YAML（按 8.5.4 节模板生成）
    kubectl apply -f deploy/k8s/mysql-shard-${i}-svc.yaml
done

echo "=== 6. 部署 Redis ==="
kubectl apply -f deploy/k8s/redis-statefulset.yaml

echo "=== 7. 等待数据库就绪 ==="
kubectl wait --for=condition=ready pod -l app=mysql-master -n $NAMESPACE --timeout=300s
kubectl wait --for=condition=ready pod -l app=mysql-slave -n $NAMESPACE --timeout=300s
for i in 0 1 2 3; do
    kubectl wait --for=condition=ready pod -l app=mysql-shard-${i} -n $NAMESPACE --timeout=300s
done
kubectl wait --for=condition=ready pod -l app=redis-cluster -n $NAMESPACE --timeout=120s

echo "=== 7b. 初始化 Redis 集群 ==="
REDIS_PODS=$(kubectl get pods -l app=redis-cluster -n $NAMESPACE \
    -o jsonpath='{range.items[*]}{.status.podIP}:6379 {end}')
kubectl exec -it redis-cluster-0 -n $NAMESPACE -- \
    redis-cli -a "$REDIS_PASSWORD" --cluster create $REDIS_PODS --cluster-replicas 1 --cluster-yes

echo "=== 8. 配置 MySQL 主从复制（自动 Job） ==="
kubectl apply -f deploy/k8s/mysql-replication-setup-job.yaml
kubectl wait --for=condition=complete job/mysql-replication-setup -n $NAMESPACE --timeout=120s

echo "=== 9. 部署 Django 应用 ==="
kubectl apply -f deploy/k8s/django-deployment.yaml
kubectl apply -f deploy/k8s/django-service.yaml
kubectl apply -f deploy/k8s/django-hpa.yaml

echo "=== 10. 部署 Celery Worker + Beat ==="
kubectl apply -f deploy/k8s/celery-deployment.yaml
kubectl apply -f deploy/k8s/celery-beat-deployment.yaml

echo "=== 11. 部署 Ingress ==="
kubectl apply -f deploy/k8s/ingress.yaml

echo "=== 12. 等待所有 Pod 就绪 ==="
kubectl wait --for=condition=ready pod -l app=django-app -n $NAMESPACE --timeout=300s

echo "=== 12. 执行拆分库 DDL（远程执行） ==="
# 在所有 MySQL 分片服务器上执行初始化 SQL
for host in 10.0.2.21 10.0.2.22 10.0.2.23 10.0.2.24; do
    echo "Initializing shard at $host..."
    ssh root@$host "docker exec mysql-shard mysql -u root -p'${MYSQL_ROOT_PASSWORD}' < /opt/init_sharding.sql"
done

echo "=== 部署完成 ==="
kubectl get all -n $NAMESPACE
echo ""
echo "Ingress External IP:"
kubectl get svc -n ingress-nginx ingress-nginx-controller
```

### 8.9 数据库 Pod 节点绑定（防止 local-path PV 数据漂移）

> **原因**: `local-path` StorageClass 将数据存在 Pod 所在节点的本地磁盘。若 Pod 漂移到其他节点，数据无法跟随。必须通过 nodeSelector 将数据库 Pod 固定到指定节点。

```bash
# 1. 在 K8s Master 上给 Worker 节点打标签
kubectl label node k8s-worker-01 node-role=mysql          # MySQL Master
kubectl label node k8s-worker-02 node-role=mysql-slave    # MySQL Slave
kubectl label node k8s-worker-03 node-role=redis          # Redis Cluster

# 2. 在所有 MySQL StatefulSet 的 spec.template.spec 中添加:
#    nodeSelector:
#      node-role: mysql           # 或 mysql-slave，按实际情况

# 3. 在 Redis StatefulSet 的 spec.template.spec 中添加:
#    nodeSelector:
#      node-role: redis
```

**以 MySQL Master 为例**，在 `deploy/k8s/mysql-master-svc.yaml` 中添加 `nodeSelector`：

```yaml
spec:
  template:
    spec:
      nodeSelector:
        node-role: mysql       # 绑定到标签为 node-role=mysql 的节点
      containers:
        - name: mysql
          # ... 其余配置不变
```

> **注意**: 如果 MySQL 分片分布在多台 Worker 上，需要为每台 Worker 打不同的标签（如 `node-role: mysql-shard-0`），再分别绑定。单机多分片时，所有分片共用同一个标签即可。

### 8.10 Django Deployment 中添加 imagePullSecrets

```yaml
spec:
  template:
    spec:
      imagePullSecrets:
        - name: harbor-registry-secret
      # ... 其余配置不变
```

同时更新镜像引用为 Harbor 地址：

```yaml
containers:
  - name: django
    image: harbor-registry:8443/enterprise-platform/django:latest   # 使用 Harbor
    imagePullPolicy: Always
```

---

## 9. Jenkins CI/CD 自动化流水线

### 9.1 Jenkins 系统配置（全局）

> **前提**: Jenkins 已部署在 jenkins-server (10.0.4.21)，参考 2.6 节

**Jenkins → Manage Jenkins → Configure System**

- **GitHub Server**: `https://github.com` → Add Credentials (GitHub Token)
- **Docker Registry**: `harbor-registry:8443` → Add Credentials → ID: `harbor-credentials`
- **Kubernetes Cloud**:
  - Kubernetes URL: `https://10.0.1.100:6443`（K8s API Server VIP）
  - Kubernetes Namespace: `jenkins-agents`
  - Credentials: Upload kubeconfig file (从 Master 节点 `/root/.kube/config` 获取)

**Jenkins → Manage Jenkins → Manage Plugins → Install**

```
Docker Pipeline
Kubernetes CLI
Kubernetes Client API
GitHub Integration
Blue Ocean
Pipeline Utility Steps
Slack Notification
SonarQube Scanner
```

**配置凭据 (Jenkins → Manage Jenkins → Credentials → System → Global credentials)**

| 凭据 ID | 类型 | 用途 |
|---------|------|------|
| `harbor-credentials` | Username/Password | Harbor 镜像仓库登录 |
| `github-token` | Secret text | GitHub 代码拉取 |
| `k8s-config` | Secret file | K8s kubectl 认证 |
| `sonarqube-token` | Secret text | SonarQube 代码扫描 |
| `slack-webhook-url` | Secret text | Slack 通知 |

**为 Jenkins Agent 创建 Namespace 和 RBAC**（在 K8s Master 执行）

```bash
kubectl create namespace jenkins-agents

kubectl create serviceaccount jenkins-agent -n jenkins-agents

kubectl create clusterrolebinding jenkins-agent-binding \
    --clusterrole=cluster-admin \
    --serviceaccount=jenkins-agents:jenkins-agent

# 获取 ServiceAccount Token
kubectl create token jenkins-agent -n jenkins-agents --duration=87600h
# 或创建长期 Secret:
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Secret
metadata:
  name: jenkins-agent-token
  namespace: jenkins-agents
  annotations:
    kubernetes.io/service-account.name: jenkins-agent
type: kubernetes.io/service-account-token
EOF
```

### 9.2 Jenkinsfile（声明式流水线）

**`deploy/jenkins/Jenkinsfile`**

```groovy
pipeline {
    agent {
        kubernetes {
            yaml '''
apiVersion: v1
kind: Pod
spec:
  containers:
    # Kaniko: 无守护进程构建镜像，无需特权模式，无需 docker.sock
    - name: kaniko
      image: gcr.io/kaniko-project/executor:v1.19.0-debug
      command: ['sleep']
      args: ['infinity']
      env:
        - name: DOCKER_CONFIG
          value: /kaniko/.docker
    - name: python
      image: python:3.11-slim
      command: ['sleep']
      args: ['infinity']
    - name: kubectl
      image: bitnami/kubectl:1.28
      command: ['sleep']
      args: ['infinity']
    - name: sonar-scanner
      image: sonarsource/sonar-scanner-cli:latest
      command: ['sleep']
      args: ['infinity']
'''
        }
    }

    environment {
        // 全局变量 - 使用 Harbor 私有仓库
        REGISTRY = 'harbor-registry:8443'
        IMAGE_NAME = 'enterprise-platform/django'
        K8S_NAMESPACE = 'enterprise-platform'
        SONAR_HOST = 'https://sonarqube.example.com'

        // 从 Jenkins 凭据获取
        DOCKER_REGISTRY_CREDS = credentials('harbor-credentials')
        GITHUB_TOKEN = credentials('github-token')
        SONAR_TOKEN = credentials('sonarqube-token')
        SLACK_WEBHOOK = credentials('slack-webhook-url')
    }

    parameters {
        // 构建参数
        choice(
            name: 'DEPLOY_ENV',
            choices: ['staging', 'production'],
            description: '部署环境'
        )
        string(
            name: 'TAG_NAME',
            defaultValue: '',
            description: '镜像 Tag（留空自动生成）'
        )
    }

    stages {

        // ==========================================
        // Stage 1: 代码检出
        // ==========================================
        stage('Checkout') {
            steps {
                checkout scm

                script {
                    // 生成镜像 Tag
                    if (params.TAG_NAME) {
                        env.IMAGE_TAG = params.TAG_NAME
                    } else {
                        env.IMAGE_TAG = "${params.DEPLOY_ENV}-${BUILD_NUMBER}-${env.GIT_COMMIT?.take(8) ?: 'latest'}"
                    }

                    // 设置构建描述
                    currentBuild.description = "Env: ${params.DEPLOY_ENV} | Tag: ${env.IMAGE_TAG}"
                }
            }
        }

        // ==========================================
        // Stage 2: 并行 - 代码质量检查
        // ==========================================
        stage('Code Quality') {
            parallel {
                stage('Lint & Type Check') {
                    steps {
                        container('python') {
                            sh '''
                                pip install flake8 mypy black isort
                                flake8 src/ --max-line-length=120 --exclude=migrations
                                black --check src/
                                isort --check-only src/
                            '''
                        }
                    }
                }

                stage('Unit Tests') {
                    steps {
                        container('python') {
                            sh '''
                                pip install -r requirements.txt
                                pip install pytest pytest-django pytest-cov pytest-xdist
                                cd src
                                python manage.py collectstatic --noinput
                                pytest --cov=. --cov-report=xml --cov-report=html \
                                       -n auto --tb=short -q apps/
                            '''
                        }
                    }
                }

                stage('Dependency Scan') {
                    steps {
                        container('python') {
                            sh '''
                                pip install safety
                                safety check -r requirements.txt --output json > safety-report.json
                            '''
                        }
                    }
                }
            }
        }

        // ==========================================
        // Stage 3: SonarQube 分析
        // ==========================================
        stage('SonarQube Analysis') {
            when {
                expression { params.DEPLOY_ENV == 'production' }
            }
            steps {
                container('sonar-scanner') {
                    withSonarQubeEnv('SonarQube') {
                        sh '''
                            sonar-scanner \
                                -Dsonar.projectKey=enterprise-platform \
                                -Dsonar.sources=src/ \
                                -Dsonar.python.coverage.reportPaths=coverage.xml \
                                -Dsonar.python.xunit.reportPath=junit.xml
                        '''
                    }
                }
            }
        }

        // ==========================================
        // Stage 4: Kaniko 构建镜像（安全方案，无需 Docker daemon）
        // ==========================================
        stage('Kaniko Build & Push') {
            steps {
                container('kaniko') {
                    script {
                        def fullImageName = "${REGISTRY}/${IMAGE_NAME}:${env.IMAGE_TAG}"

                        // Kaniko: 无需 docker daemon，无需特权模式
                        // 从 Harbor 拉取时会自动使用 /kaniko/.docker/config.json 中的凭据
                        sh """
                            # 创建 Docker config（Harbor 认证）
                            mkdir -p /kaniko/.docker
                            AUTH=\$(echo -n "${DOCKER_REGISTRY_CREDS_USR}:${DOCKER_REGISTRY_CREDS_PSW}" | base64 -w0)
                            cat > /kaniko/.docker/config.json <<DOCKERCONF
{
  "auths": {
    "${REGISTRY}": {
      "auth": "\${AUTH}"
    }
  }
}
DOCKERCONF

                            # Kaniko 构建并推送
                            /kaniko/executor \
                                --context=dir://\$(pwd) \
                                --dockerfile=deploy/docker/Dockerfile \
                                --destination=${fullImageName} \
                                --destination=${REGISTRY}/${IMAGE_NAME}:${params.DEPLOY_ENV}-latest \
                                --cache=true \
                                --cache-ttl=24h \
                                --skip-tls-verify \
                                --insecure-registry=${REGISTRY}
                        """
                    }
                }
            }
        }

        // ==========================================
        // Stage 5: 推送到 Staging 环境
        // ==========================================
        stage('Deploy to Staging') {
            when {
                expression { params.DEPLOY_ENV == 'staging' }
            }
            steps {
                container('kubectl') {
                    script {
                        sh """
                            kubectl set image deployment/django-app \
                                django=${REGISTRY}/${IMAGE_NAME}:${env.IMAGE_TAG} \
                                -n ${K8S_NAMESPACE}-staging --record

                            kubectl rollout status deployment/django-app \
                                -n ${K8S_NAMESPACE}-staging --timeout=300s
                        """
                    }
                }
            }
        }

        // ==========================================
        // Stage 6: 生产部署（金丝雀发布）
        // ==========================================
        stage('Canary Deploy') {
            when {
                expression { params.DEPLOY_ENV == 'production' }
            }
            steps {
                container('kubectl') {
                    script {
                        // 步骤 1: 部署金丝雀版本（10% 流量）
                        sh """
                            kubectl apply -f deploy/k8s/django-canary-deployment.yaml \
                                -n ${K8S_NAMESPACE}
                            kubectl set image deployment/django-canary \
                                django=${REGISTRY}/${IMAGE_NAME}:${env.IMAGE_TAG} \
                                -n ${K8S_NAMESPACE}
                        """

                        // 步骤 2: 等待金丝雀就绪
                        sh """
                            kubectl wait --for=condition=available \
                                deployment/django-canary \
                                -n ${K8S_NAMESPACE} --timeout=120s
                        """

                        // 步骤 3: 人工确认（健康检查通过后）
                        input message: "金丝雀版本已运行 5 分钟，是否继续全量发布？",
                              ok: "全量发布",
                              submitter: 'admin,tech-lead'
                    }
                }
            }
        }

        // ==========================================
        // Stage 7: 全量发布
        // ==========================================
        stage('Full Rollout') {
            when {
                expression { params.DEPLOY_ENV == 'production' }
            }
            steps {
                container('kubectl') {
                    script {
                        sh """
                            # 更新正式 Deployment
                            kubectl set image deployment/django-app \
                                django=${REGISTRY}/${IMAGE_NAME}:${env.IMAGE_TAG} \
                                -n ${K8S_NAMESPACE} --record

                            # 滚动更新
                            kubectl rollout status deployment/django-app \
                                -n ${K8S_NAMESPACE} --timeout=600s

                            # 更新 Celery Worker
                            kubectl set image deployment/celery-worker \
                                celery-worker=${REGISTRY}/${IMAGE_NAME}:${env.IMAGE_TAG} \
                                -n ${K8S_NAMESPACE}
                        """
                    }
                }
            }
        }

        // ==========================================
        // Stage 8: 冒烟测试
        // ==========================================
        stage('Smoke Tests') {
            when {
                expression { params.DEPLOY_ENV == 'production' }
            }
            steps {
                container('python') {
                    sh '''
                        pip install requests

                        python -c "
import requests, sys

BASE = 'https://api.example.com'

# 1. 健康检查
r = requests.get(f'{BASE}/health/', timeout=10)
assert r.status_code == 200, f'Health check failed: {r.status_code}'
print('[PASS] Health check')

# 2. API 测试
r = requests.get(f'{BASE}/api/v1/products/', timeout=10)
assert r.status_code == 200, f'API test failed: {r.status_code}'
print('[PASS] API test')

print('All smoke tests passed!')
"
                    '''
                }
            }
        }

        // ==========================================
        // Stage 9: 数据库迁移（如需要）
        // ==========================================
        stage('DB Migration') {
            when {
                expression { params.DEPLOY_ENV == 'production' }
            }
            steps {
                container('kubectl') {
                    script {
                        def shouldMigrate = input(
                            message: '是否需要执行数据库迁移？',
                            parameters: [
                                booleanParam(
                                    name: 'RUN_MIGRATION',
                                    defaultValue: false,
                                    description: '执行 Django migrate'
                                )
                            ]
                        )

                        if (shouldMigrate) {
                            sh """
                                kubectl exec deployment/django-app -n ${K8S_NAMESPACE} -- \
                                    python manage.py migrate --noinput
                            """
                        }
                    }
                }
            }
        }
    }

    post {
        always {
            // 清理工作空间
            cleanWs()

            // 归档测试报告
            archiveArtifacts artifacts: '**/coverage.xml, **/junit.xml, **/safety-report.json',
                             allowEmptyArchive: true

            // 发布 JUnit 报告
            junit '**/junit.xml'
        }

        success {
            // 成功通知
            script {
                def message = """
                ✅ *部署成功*
                - 环境: ${params.DEPLOY_ENV}
                - 版本: ${env.IMAGE_TAG}
                - 构建号: #${BUILD_NUMBER}
                - 耗时: ${currentBuild.durationString}
                - 构建链接: ${env.BUILD_URL}
                """.stripIndent()

                slackSend(
                    color: 'good',
                    message: message,
                    channel: '#deploy-notifications'
                )
            }

            // Git Tag
            script {
                if (params.DEPLOY_ENV == 'production') {
                    sh """
                        git tag -a "release-${env.IMAGE_TAG}" -m "Release ${env.IMAGE_TAG}"
                        git push origin "release-${env.IMAGE_TAG}"
                    """
                }
            }
        }

        failure {
            // 失败通知
            script {
                def message = """
                ❌ *部署失败*
                - 环境: ${params.DEPLOY_ENV}
                - 版本: ${env.IMAGE_TAG}
                - 构建号: #${BUILD_NUMBER}
                - 阶段: ${env.STAGE_NAME}
                - 构建链接: ${env.BUILD_URL}
                """.stripIndent()

                slackSend(
                    color: 'danger',
                    message: message,
                    channel: '#deploy-alerts'
                )
            }

            // 自动回滚
            script {
                if (params.DEPLOY_ENV == 'production') {
                    sh """
                        kubectl rollout undo deployment/django-app -n ${K8S_NAMESPACE}
                        kubectl rollout undo deployment/celery-worker -n ${K8S_NAMESPACE}
                    """
                    slackSend(
                        color: 'warning',
                        message: "⚠️ 已自动回滚到上一个版本",
                        channel: '#deploy-alerts'
                    )
                }
            }
        }
    }
}
```

### 9.3 Jenkins 创建流水线任务

```bash
# 方式一: Jenkins UI 创建
# New Item → Pipeline → 名称 "enterprise-platform-pipeline"
# Pipeline → Definition: Pipeline script from SCM
# SCM: Git
# Repository URL: https://github.com/your-org/enterprise-platform.git
# Script Path: deploy/jenkins/Jenkinsfile

# 方式二: Jenkins CLI 创建
java -jar jenkins-cli.jar -s http://jenkins.example.com \
    create-job enterprise-platform-pipeline < pipeline-config.xml
```

**`deploy/jenkins/pipeline-config.xml`**

```xml
<?xml version='1.1' encoding='UTF-8'?>
<flow-definition plugin="workflow-job@2.42">
  <description>Enterprise Platform CI/CD Pipeline</description>
  <keepDependencies>false</keepDependencies>
  <definition class="org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition" plugin="workflow-cps@2.93">
    <scm class="hudson.plugins.git.GitSCM" plugin="git@4.12.0">
      <configVersion>2</configVersion>
      <userRemoteConfigs>
        <hudson.plugins.git.UserRemoteConfig>
          <url>https://github.com/your-org/enterprise-platform.git</url>
          <credentialsId>github-token</credentialsId>
        </hudson.plugins.git.UserRemoteConfig>
      </userRemoteConfigs>
      <branches>
        <hudson.plugins.git.BranchSpec>
          <name>*/main</name>
        </hudson.plugins.git.BranchSpec>
      </branches>
    </scm>
    <scriptPath>deploy/jenkins/Jenkinsfile</scriptPath>
    <lightweight>true</lightweight>
  </definition>
  <triggers>
    <hudson.triggers.SCMTrigger>
      <spec>H/5 * * * *</spec>  <!-- 每 5 分钟轮询 -->
    </hudson.triggers.SCMTrigger>
  </triggers>
</flow-definition>
```

### 9.4 多分支流水线（GitHub Webhook 触发）

```groovy
// 另一种方式: 多分支流水线
// 在 Jenkins 中创建 Multibranch Pipeline
// Branch Sources → GitHub → 选择仓库
// Build Configuration → by Jenkinsfile

// 每次 PR 自动运行测试
// 每次合并到 main 自动部署 staging
// tag push 手动触发 production 部署
```

---

## 10. 监控与日志

### 10.1 Prometheus + Grafana 监控

#### 10.1.0 安装 kube-prometheus-stack（Prometheus Operator + Grafana + Alertmanager）

```bash
# ============================================
# 在 K8s Master 执行
# ============================================

# 1. 添加 Helm 仓库
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# 2. 创建 monitoring 命名空间
kubectl create namespace monitoring

# 3. 安装 kube-prometheus-stack（包含 Prometheus Operator + Grafana + Node Exporter + kube-state-metrics）
helm upgrade --install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
    --namespace monitoring \
    --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false \
    --set prometheus.prometheusSpec.podMonitorSelectorNilUsesHelmValues=false \
    --set grafana.adminPassword=GrafanaAdmin2024

# 4. 等待所有 Pod 就绪
kubectl wait --for=condition=ready pod \
    -l app.kubernetes.io/name=grafana -n monitoring --timeout=120s
kubectl wait --for=condition=ready pod \
    -l app=prometheus -n monitoring --timeout=120s

# 5. Grafana 访问
kubectl get svc -n monitoring kube-prometheus-stack-grafana
# 修改为 LoadBalancer 类型获取外部 IP:
kubectl patch svc kube-prometheus-stack-grafana -n monitoring \
    -p '{"spec": {"type": "LoadBalancer"}}'
# 访问 http://<EXTERNAL-IP>  用户名: admin  密码: GrafanaAdmin2024

# 6. Prometheus 访问
kubectl patch svc kube-prometheus-stack-prometheus -n monitoring \
    -p '{"spec": {"type": "LoadBalancer"}}'
```

#### 10.1.1 自定义 Prometheus 采集配置

如果您还需要额外的 scrape 目标（如非 K8s 管理的 MySQL/Redis），补充以下配置：

**`deploy/k8s/monitoring/prometheus-additional-scrape.yaml`**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: monitoring
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
      evaluation_interval: 15s

    scrape_configs:
      - job_name: 'django-app'
        kubernetes_sd_configs:
          - role: pod
            namespaces:
              names:
                - enterprise-platform
        relabel_configs:
          - source_labels: [__meta_kubernetes_pod_label_app]
            action: keep
            regex: django-app

      - job_name: 'mysql'
        static_configs:
          - targets:
              - mysql-shard-0-service:9104
              - mysql-shard-1-service:9104
              - mysql-shard-2-service:9104
              - mysql-shard-3-service:9104

      - job_name: 'redis'
        static_configs:
          - targets:
              - redis-metrics-service:9121

      - job_name: 'nginx-ingress'
        kubernetes_sd_configs:
          - role: pod
            namespaces:
              names:
                - ingress-nginx
```

### 10.2 Django Prometheus Metrics

**`src/config/settings/base.py` 追加:**

```python
# Prometheus 监控
INSTALLED_APPS += ['django_prometheus']

MIDDLEWARE.insert(0, 'django_prometheus.middleware.PrometheusBeforeMiddleware')
MIDDLEWARE.append('django_prometheus.middleware.PrometheusAfterMiddleware')

# 在 urls.py 中:
# urlpatterns.append(path('', include('django_prometheus.urls')))
```

**`requirements.txt` 追加:**

```
django-prometheus==2.3.1
```

### 10.3 ELK 日志采集

**`deploy/k8s/logging/filebeat-config.yaml`**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: filebeat-config
  namespace: enterprise-platform
data:
  filebeat.yml: |
    filebeat.inputs:
      - type: container
        paths:
          - /var/log/containers/django-*.log
        json.keys_under_root: true
        json.add_error_key: true
        processors:
          - add_kubernetes_metadata:
              host: ${NODE_NAME}
              matchers:
                - logs_path:
                    logs_path: "/var/log/containers/"

    output.elasticsearch:
      hosts: ['elasticsearch-master:9200']
      index: "django-logs-%{+yyyy.MM.dd}"

    # 或者输出到 Kafka 作为中间缓冲
    # output.kafka:
    #   hosts: ['kafka-broker-0:9092']
    #   topic: 'django-logs'

    setup.template.name: "django-logs"
    setup.template.pattern: "django-logs-*"
```

### 10.4 告警规则

**`deploy/k8s/monitoring/alert-rules.yaml`**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-alert-rules
  namespace: monitoring
data:
  alerts.yml: |
    groups:
      - name: django-app
        rules:
          - alert: HighErrorRate
            expr: rate(django_http_responses_total_by_status_view{status=~"5.."}[5m]) > 0.05
            for: 5m
            labels:
              severity: critical
            annotations:
              summary: "Django 5xx 错误率超过 5%"
              description: "5xx 错误率: {{ $value | humanizePercentage }}"

          - alert: HighLatency
            expr: histogram_quantile(0.95, rate(django_http_request_duration_seconds_bucket[5m])) > 1
            for: 5m
            labels:
              severity: warning
            annotations:
              summary: "P95 延迟超过 1 秒"

          - alert: PodRestarting
            expr: rate(kube_pod_container_status_restarts_total{namespace="enterprise-platform"}[15m]) > 0
            for: 5m
            labels:
              severity: warning
            annotations:
              summary: "Pod 频繁重启"

          - alert: HPAReachingLimit
            expr: kube_hpa_status_current_replicas{namespace="enterprise-platform"} >= kube_hpa_spec_max_replicas
            for: 10m
            labels:
              severity: warning
            annotations:
              summary: "HPA 达到最大副本数"
```

---

## 附录

### A. 常用运维命令

```bash
# === 服务器管理 ===
ssh root@k8s-master-01                                         # SSH 到 K8s Master
ansible all -i inventory.ini -m ping                           # Ansible 批量检查
for host in k8s-master-01 k8s-worker-01; do ssh root@$host "uptime"; done

# === Docker ===
# 注意: Docker Compose 分散在各服务器上，在对应服务器执行
ssh root@mysql-master "docker compose -f /opt/mysql/docker-compose.yml ps"
ssh root@mysql-master "docker compose -f /opt/mysql/docker-compose.yml logs -f"
ssh root@redis-node-0 "docker ps | grep redis"

# === Harbor 仓库 ===
# 访问 https://harbor-registry:8443
docker login harbor-registry:8443 -u admin -p Harbor12345
docker tag myimage:latest harbor-registry:8443/enterprise-platform/myimage:v1.0
docker push harbor-registry:8443/enterprise-platform/myimage:v1.0
# 查看镜像仓库
curl -u admin:Harbor12345 https://harbor-registry:8443/api/v2.0/projects
# 清理旧镜像（Harbor GC）
ssh root@harbor-registry "docker exec harbor-jobservice /harbor/harbor_registryctl garbage-collect"

# === Kubernetes ===
kubectl get pods -n enterprise-platform                        # 查看 Pod
kubectl logs -f <pod-name> -n enterprise-platform --tail=100  # 查看日志
kubectl exec -it <pod-name> -n enterprise-platform -- bash    # 进入容器
kubectl describe pod <pod-name> -n enterprise-platform        # Pod 详情
kubectl top pods -n enterprise-platform                       # 资源使用
kubectl top nodes                                             # 节点资源

# 扩缩容
kubectl scale deployment django-app --replicas=5 -n enterprise-platform

# 滚动发布与回滚
kubectl set image deployment/django-app \
    django=harbor-registry:8443/enterprise-platform/django:v1.1.0 \
    -n enterprise-platform --record
kubectl rollout status deployment/django-app -n enterprise-platform --timeout=300s
kubectl rollout history deployment/django-app -n enterprise-platform
kubectl rollout undo deployment/django-app -n enterprise-platform

# 查看 Ingress 状态
kubectl get ingress -n enterprise-platform
kubectl describe ingress enterprise-ingress -n enterprise-platform

# === Django Management ===
kubectl exec -it deployment/django-app -n enterprise-platform -- python manage.py shell
kubectl exec -it deployment/django-app -n enterprise-platform -- python manage.py showmigrations
kubectl exec -it deployment/django-app -n enterprise-platform -- python manage.py createsuperuser

# === MySQL ===
# 连接主库
ssh root@mysql-master "docker exec mysql-master mysql -u root -p"
# 连接分片(以 shard-0 为例)
ssh root@mysql-shard-0 "docker exec mysql-shard mysql -u root -p enterprise_order_0"
# 检查主从同步
ssh root@mysql-slave "docker exec mysql-slave mysql -u root -p -e 'SHOW SLAVE STATUS\G'"
# 检查分片数据分布
echo "SELECT user_id % 4 AS shard, COUNT(*) FROM order_info GROUP BY shard;" \
    | ssh root@mysql-shard-0 "docker exec -i mysql-shard mysql -u root -p enterprise_order_0"

# === Redis ===
ssh root@redis-node-0 "docker exec redis-cluster redis-cli -a RedisPass789! cluster info"
ssh root@redis-node-0 "docker exec redis-cluster redis-cli -a RedisPass789! info memory"
ssh root@redis-node-0 "docker exec redis-cluster redis-cli -a RedisPass789! dbsize"

# === Jenkins ===
# 重启 Jenkins
ssh root@jenkins-server "cd /opt/jenkins && docker compose restart"
# 查看 Jenkins 日志
ssh root@jenkins-server "docker logs -f jenkins --tail 100"
# 备份 Jenkins 数据
ssh root@jenkins-server "tar czf /backup/jenkins-\$(date +%Y%m%d).tar.gz -C /data jenkins"

# === 备份 ===
# MySQL 全量备份（在主库执行）
ssh root@mysql-master "docker exec mysql-master mysqldump -u root -p \
    --all-databases --single-transaction --quick --lock-tables=false \
    | gzip > /backup/mysql-full-\$(date +%Y%m%d-%H%M).sql.gz"
```

### B. Makefile（开发辅助）

```makefile
.PHONY: dev build push deploy-staging deploy-production test lint clean

# 本地开发
dev:
	docker run -d --name dev-mysql -e MYSQL_ROOT_PASSWORD=devpass -p 3306:3306 mysql:8.0
	docker run -d --name dev-redis -p 6379:6379 redis:7.0-alpine
	cd src && python manage.py runserver 0.0.0.0:8000

# 构建 Docker 镜像
build:
	docker build -t harbor-registry:8443/enterprise-platform/django:latest \
		-f deploy/docker/Dockerfile .

# 推送镜像到 Harbor
push: build
	docker login harbor-registry:8443 -u admin -p Harbor12345
	docker push harbor-registry:8443/enterprise-platform/django:latest

# 运行测试
test:
	cd src && pytest --cov=. --cov-report=term-missing -n auto

# 代码检查
lint:
	flake8 src/ --max-line-length=120 --exclude=migrations
	black --check src/
	isort --check-only src/

# 格式化
format:
	black src/
	isort src/

# 部署到 K8s staging
deploy-staging:
	kubectl apply -f deploy/k8s/django-deployment.yaml -n enterprise-platform-staging
	kubectl set image deployment/django-app \
		django=harbor-registry:8443/enterprise-platform/django:staging-latest \
		-n enterprise-platform-staging

# 部署到 K8s production
deploy-production:
	bash deploy/k8s/deploy-all.sh

# 清理
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	docker system prune -f
```

### C. 安全检查清单

- [ ] Django `SECRET_KEY` 使用环境变量，不硬编码
- [ ] `DEBUG=False` 在生产环境
- [ ] 数据库密码使用 K8s Secret，不提交 Git
- [ ] HTTPS 强制启用（`SECURE_SSL_REDIRECT`）
- [ ] JWT Token 设置合理过期时间
- [ ] CORS 白名单限制来源域名
- [ ] API 限流配置（Throttling）
- [ ] SQL 注入防护（ORM 参数化查询）
- [ ] XSS 防护（模板自动转义 + CSP 头）
- [ ] CSRF 防护启用
- [ ] 容器以非 root 用户运行
- [ ] Docker 镜像定期扫描漏洞（Trivy/Clair）
- [ ] K8s NetworkPolicy 限制 Pod 间通信
- [ ] K8s Pod Security Policy / Security Context
- [ ] 敏感配置使用 K8s Secret + 加密存储
- [ ] 定期备份数据库（Velero/CronJob）
- [ ] 日志脱敏（不记录密码/Token）

---

> **文档版本**: v2.0
> **最后更新**: 2026-06-01
> **部署环境**: 物理服务器 / 自建机房 / 私有云
> **技术栈**: Python 3.11 / Django 4.2 / MySQL 8.0 / Redis 7.0 / Docker 24.x / Harbor 2.9 / K8s 1.28 (kubeadm) / Jenkins 2.426
