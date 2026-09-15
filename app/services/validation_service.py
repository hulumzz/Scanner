from datetime import date


def issue(code,message,field_name=None,severity='ERROR',row=None): return {'code':code,'message':message,'field_name':field_name,'severity':severity,'row':row}


def validate_extraction(header,members,row_mismatches):
    issues=[]; no_kk=(header.no_kk or '').strip()
    if len(no_kk)!=16 or not no_kk.isdigit(): issues.append(issue('INVALID_KK_NUMBER','Nomor KK harus terdiri dari tepat 16 digit.','no_kk','CRITICAL'))
    rows=[m.no_urut_kk for m in members]
    if len(rows)!=len(set(rows)): issues.append(issue('ROW_MISMATCH','Nomor urut anggota terduplikasi.','no_urut_kk','CRITICAL'))
    for row in row_mismatches: issues.append(issue('ROW_MISMATCH',f'Baris {row} tidak ditemukan pada salah satu tabel KK.','row','CRITICAL',row))
    seen=set(); heads=0
    for m in members:
        nik=(m.nik or '').strip()
        if len(nik)!=16 or not nik.isdigit(): issues.append(issue('INVALID_NIK',f'NIK anggota baris {m.no_urut_kk} harus 16 digit.','nik','ERROR',m.no_urut_kk))
        elif nik in seen: issues.append(issue('DUPLICATE_NIK',f'NIK pada baris {m.no_urut_kk} terduplikasi dalam KK.','nik','CRITICAL',m.no_urut_kk))
        else: seen.add(nik)
        if m.tanggal_lahir and m.tanggal_lahir>date.today(): issues.append(issue('INVALID_DATE',f'Tanggal lahir baris {m.no_urut_kk} berada di masa depan.','tanggal_lahir','ERROR',m.no_urut_kk))
        if not m.tanggal_lahir: issues.append(issue('INVALID_DATE',f'Tanggal lahir baris {m.no_urut_kk} tidak terbaca atau tidak valid.','tanggal_lahir','WARNING',m.no_urut_kk))
        if (m.status_hubungan or '').strip().lower()=='kepala keluarga': heads+=1
        if not m.nama_lengkap: issues.append(issue('UNREADABLE_FIELD',f'Nama lengkap baris {m.no_urut_kk} tidak terbaca.','nama_lengkap','ERROR',m.no_urut_kk))
    if heads>1: issues.append(issue('MULTIPLE_HEADS','Terdapat lebih dari satu anggota berstatus Kepala Keluarga.','status_hubungan','CRITICAL'))
    if heads==0: issues.append(issue('UNREADABLE_FIELD','Kepala Keluarga tidak dapat ditentukan dari tabel.','status_hubungan','WARNING'))
    return issues
