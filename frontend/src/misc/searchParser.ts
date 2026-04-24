export type SortBy = 'name' | 'quantity' | 'brand' | 'id';
export type SortDir = 'asc' | 'desc';

export const SORT_LABELS: Record<SortBy, string> = { name: 'Name', quantity: 'Qty', brand: 'Brand', id: 'ID'};

export type ParseResult = { search?: string; id?: string; name?: string; brand?: string; tag?: string; quantity?: string; error?: string };

export function parseSearch(raw: string): ParseResult {
    const segments = raw.split(',').map(s => s.trim()).filter(Boolean);
    let id: string | undefined;
    let name: string | undefined;
    let brand: string | undefined;
    let tag: string | undefined;
    let quantity: string | undefined;
    const searchParts: string[] = [];
    const seen = new Set<string>();

    for (const seg of segments) {
        const im = seg.match(/^id:(\d+)$/i);
        if (im) { if (!seen.has('id')) { seen.add('id'); id = im[1]; } continue; }
        if (/^id:$/i.test(seg)) return { error: '"id:" requires a numeric value' };
        if (/^id:[^\d]/i.test(seg)) return { error: '"id:" requires a numeric value' };

        const nm = seg.match(/^name:(.+)$/i);
        if (nm) { if (!seen.has('name')) { seen.add('name'); name = `%${nm[1].trim()}%`; } continue; }
        if (/^name:$/i.test(seg)) return { error: '"name:" requires a value' };

        const bm = seg.match(/^brand:(.+)$/i);
        if (bm) { if (!seen.has('brand')) { seen.add('brand'); brand = `%${bm[1].trim()}%`; } continue; }
        if (/^brand:$/i.test(seg)) return { error: '"brand:" requires a value' };

        const tm = seg.match(/^tag:(.+)$/i);
        if (tm) { if (!seen.has('tag')) { seen.add('tag'); tag = `%${tm[1].trim()}%`; } continue; }
        if (/^tag:$/i.test(seg)) return { error: '"tag:" requires a value' };

        if (/^qty/i.test(seg)) {
            if (!seen.has('qty')) {
                const r   = seg.match(/^qty:(\d+)-(\d+)$/i);
                if (r)   { seen.add('qty'); quantity = `${r[1]}:${r[2]}`; continue; }
                const gte = seg.match(/^qty>=(\d+)$/i);
                if (gte) { seen.add('qty'); quantity = `${gte[1]}:`; continue; }
                const lte = seg.match(/^qty<=(\d+)$/i);
                if (lte) { seen.add('qty'); quantity = `:${lte[1]}`; continue; }
                const gt  = seg.match(/^qty>(\d+)$/i);
                if (gt)  { seen.add('qty'); quantity = `${parseInt(gt[1]) + 1}:`; continue; }
                const lt  = seg.match(/^qty<(\d+)$/i);
                if (lt)  { seen.add('qty'); const n = parseInt(lt[1]) - 1; quantity = `:${Math.max(0, n)}`; continue; }
                const eq  = seg.match(/^qty[=:](\d+)$/i);
                if (eq)  { seen.add('qty'); quantity = eq[1]; continue; }
                return { error: `Invalid qty expression "${seg}" — try: qty=N, qty>N, qty<N, qty>=N, qty<=N, qty:N-M` };
            }
            continue;
        }

        if (/^[a-zA-Z]+:/.test(seg)) {
            return { error: `Unknown filter "${seg.split(':')[0]}:" — valid filters: id:, name:, brand:, tag:, qty` };
        }

        searchParts.push(seg);
    }

    return {
        search: searchParts.join(' ').trim() || undefined,
        id: id || undefined,
        name: name || undefined,
        brand: brand || undefined,
        tag,
        quantity,
    };
}
