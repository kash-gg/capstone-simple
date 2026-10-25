const $ = id => document.getElementById(id);
async function request(path, options) {
  const response = await fetch(path, {...options, signal: AbortSignal.timeout(10000)});
  const data = await response.json();
  if (!response.ok) throw new Error(typeof data.detail === 'string' ? data.detail : `Request failed (${response.status}). Check payment details.`);
  return data;
}
function node(tag, text, className) {
  const element = document.createElement(tag);
  if (text !== undefined) element.textContent = text;
  if (className) element.className = className;
  return element;
}
async function refresh() {
  $('refresh').disabled = true;
  $('table-status').textContent = 'Loading payments...';
  try {
    const [health, payments, notifications] = await Promise.all([request('/health'), request('/api/payments'), request('/api/notifications')]);
    $('health').textContent = `Backend ${health.status} / ${health.version}`;
    $('health').className = 'badge';
    $('total').textContent = payments.length;
    for (const status of ['COMPLETED', 'PENDING', 'FAILED']) $(status.toLowerCase()).textContent = payments.filter(p => p.status === status).length;
    $('payments').replaceChildren(...payments.map(p => {
      const row = node('tr');
      const parties = node('td', p.payer); parties.append(node('small', `to ${p.payee}`));
      const state = node('td'); state.append(node('span', p.status, `status ${p.status}`));
      row.append(node('td', `PAY-${String(p.id).padStart(4, '0')}`), parties, node('td', `${p.currency} ${Number(p.amount).toFixed(2)}`), state, node('td', new Date(p.created_at).toLocaleString()));
      return row;
    }));
    $('table-status').className = '';
    $('table-status').textContent = payments.length ? `${payments.length} payments / latest first` : 'No payments yet. Create your first payment above.';
    $('notifications').replaceChildren(...(notifications.length ? notifications.map(n => {
      const item = node('li', n.message); item.append(node('small', new Date(n.created_at).toLocaleString())); return item;
    }) : [node('li', 'No notifications yet.')]));
  } catch (error) {
    $('health').textContent = 'Backend unavailable'; $('health').className = 'badge error';
    $('table-status').textContent = `Unable to refresh: ${error.message}`; $('table-status').className = 'error-text';
    $('notifications').replaceChildren(node('li', 'Notifications unavailable. Try refreshing.'));
  } finally { $('refresh').disabled = false; }
}
$('refresh').addEventListener('click', refresh);
$('payment-form').addEventListener('submit', async event => {
  event.preventDefault();
  const button = event.target.querySelector('button'); button.disabled = true;
  $('form-status').textContent = 'Submitting payment...'; $('form-status').className = '';
  try {
    const data = Object.fromEntries(new FormData(event.target));
    const payment = await request('/api/payments', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data)});
    $('form-status').textContent = `Payment #${payment.id} created successfully.`;
    event.target.reset(); await refresh();
  } catch (error) { $('form-status').textContent = error.message; $('form-status').className = 'error-text'; }
  finally { button.disabled = false; }
});
refresh();
