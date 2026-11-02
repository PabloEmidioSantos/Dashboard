const $ = (selector, root = document) => root.querySelector(selector);
const authView = $('#authView');
const dashboardView = $('#dashboardView');
const authCard = $('.auth-card');
let authMode = 'login';
let pendingPayments = [];

const api = async (path, options = {}) => {
  const response = await fetch(path, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) }
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || 'Ocorreu um erro');
  return data;
};

const money = value => Number(value || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
const show = view => {
  [authView, dashboardView].forEach(item => item.classList.toggle('active', item === view));
};

const authorizedHeaders = () => ({ Authorization: `Bearer ${localStorage.getItem('sessionToken')}` });

document.querySelectorAll('.tab').forEach(tab => tab.addEventListener('click', () => {
  authMode = tab.dataset.auth;
  document.querySelectorAll('.tab').forEach(item => item.classList.toggle('active', item === tab));
  authCard.classList.toggle('register', authMode === 'register');
  $('#authSubmit').textContent = authMode === 'register' ? 'Criar conta' : 'Entrar';
  $('[name=password]').autocomplete = authMode === 'register' ? 'new-password' : 'current-password';
  $('#authMessage').textContent = '';
}));

$('#authForm').addEventListener('submit', async event => {
  event.preventEvent = event.preventDefault();
  event.preventDefault();
  const form = Object.fromEntries(new FormData(event.currentTarget));
  $('#authMessage').textContent = 'Processando…';
  try {
    const result = await api(`/api/${authMode}`, { method: 'POST', body: JSON.stringify(form) });
    localStorage.setItem('sessionToken', result.token);
    await openDashboard();
  } catch (error) {
    $('#authMessage').textContent = error.message;
  }
});

async function openDashboard() {
  try {
    const data = await api('/api/dashboard', { headers: authorizedHeaders() });
    $('#welcome').textContent = `Olá, ${data.name}`;
    $('#balance').textContent = money(data.balance);
    $('#balance').className = data.balance >= 0 ? 'positive' : 'negative';
    $('#balanceStatus').textContent = data.balance >= 0 ? 'Saldo positivo' : 'Atenção aos gastos';
    $('#income').textContent = money(data.income);
    $('#expenses').textContent = money(data.expenses);
    const form = $('#financeForm');
    ['income', 'water', 'electricity', 'internet'].forEach(name => form.elements[name].value = name === 'income' ? data[name] || '' : data.mandatory[name] || '');
    pendingPayments = data.pending || [];
    renderPending();
    show(dashboardView);
  } catch {
    localStorage.removeItem('sessionToken');
    show(authView);
  }
}

function renderPending() {
  $('#pendingList').innerHTML = pendingPayments.map((payment, index) => `
    <div class="pending-item">
      <div class="field"><input aria-label="Descrição do pagamento" placeholder="Ex.: Aluguel" value="${escapeHTML(payment.name || '')}" data-index="${index}" data-field="name"></div>
      <div class="money-input"><span>R$</span><input aria-label="Valor" type="number" min="0" step="0.01" value="${payment.amount || ''}" data-index="${index}" data-field="amount"></div>
      <button type="button" class="remove-payment" data-remove="${index}" aria-label="Remover">×</button>
    </div>`).join('');
}

function escapeHTML(value) {
  const element = document.createElement('div');
  element.textContent = value;
  return element.innerHTML;
}

$('#pendingList').addEventListener('input', event => {
  const index = Number(event.target.dataset.index);
  if (Number.isNaN(index)) return;
  pendingPayments[index][event.target.dataset.field] = event.target.dataset.field === 'amount' ? Number(event.target.value) : event.target.value;
});

$('#pendingList').addEventListener('click', event => {
  const button = event.target.closest('[data-remove]');
  if (!button) return;
  pendingPayments.splice(Number(button.dataset.remove), 1);
  renderPending();
});

$('#addPayment').addEventListener('click', () => {
  pendingPayments.push({ name: '', amount: 0 });
  renderPending();
  $('#pendingList').lastElementChild?.scrollIntoView({ behavior: 'smooth', block: 'center' });
});

$('#financeForm').addEventListener('submit', async event => {
  event.preventDefault();
  const form = Object.fromEntries(new FormData(event.currentTarget));
  const pending = pendingPayments.filter(item => item.name?.trim() && Number(item.amount) >= 0);
  try {
    await api('/api/finances', { method: 'POST', headers: authorizedHeaders(), body: JSON.stringify({ ...form, pending }) });
    await openDashboard();
    const button = $('.save-button');
    button.textContent = 'Salvo com sucesso';
    setTimeout(() => button.textContent = 'Salvar movimentação', 1600);
  } catch (error) {
    alert(error.message);
  }
});

$('#logout').addEventListener('click', () => {
  localStorage.removeItem('sessionToken');
  show(authView);
});

if (localStorage.getItem('sessionToken')) openDashboard(); else show(authView);
