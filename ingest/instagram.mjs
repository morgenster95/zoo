// Tenký klient Instagram Graph API (graph.facebook.com, systémový token z firemního portfolia, jako ve frontě).
// Žádná tajemství v kódu: token a ID jdou z prostředí. `fetchImpl` jde podstrčit pro testy.
export class Instagram {
  constructor({ token, userId, host = 'graph.facebook.com', version = 'v23.0', fetchImpl = fetch } = {}) {
    if (!token || !userId) throw new Error('Chybí IG_ACCESS_TOKEN nebo IG_USER_ID');
    Object.assign(this, { token, userId, base: `https://${host}/${version}`, f: fetchImpl });
  }
  async get(path, params = {}) {
    const url = new URL(path.startsWith('http') ? path : `${this.base}/${path}`);
    for (const [k, v] of Object.entries(params)) url.searchParams.set(k, v);
    if (!url.searchParams.has('access_token')) url.searchParams.set('access_token', this.token);
    const j = await (await this.f(url)).json();
    if (j.error) throw new Error(`IG ${path}: ${j.error.message}`);
    return j;
  }
  async post(path, body) {
    const r = await this.f(`${this.base}/${path}`, { method: 'POST', headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${this.token}` }, body: JSON.stringify(body) });
    const j = await r.json();
    if (j.error) throw new Error(`IG POST ${path}: ${j.error.message}`);
    return j;
  }
  profile() { return this.get(this.userId, { fields: 'username,followers_count,media_count' }); }
  async recentMedia(limit = 5) { return (await this.get(`${this.userId}/media`, { fields: 'id,caption,permalink,timestamp,media_type', limit })).data || []; }
  /** všechny komentáře k příspěvku (stránkování, max `max`), s lajky; odpovědi mají parent_id */
  async comments(mediaId, max = 500) {
    let url = `${mediaId}/comments`, params = { fields: 'id,text,username,timestamp,like_count,parent_id', limit: 100 };
    const out = [];
    while (url && out.length < max) {
      const j = await this.get(url, params);
      out.push(...(j.data || []));
      url = j.paging?.next || null; params = {};
    }
    return out;
  }
  reply(commentId, message) { return this.post(`${commentId}/replies`, { message }); }
}
