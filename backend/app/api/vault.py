"""Secure Vault endpoints: password-protected, encrypted file storage."""
from __future__ import annotations

import base64
import os
from pathlib import Path
from typing import Annotated
from uuid import UUID

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import Response
from pydantic import Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import User, VaultFile
from app.schemas.schemas import VaultDownloadRequest, VaultFileOut

router = APIRouter(prefix="/vault", tags=["vault"])

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
VAULT_DIR: str = os.environ.get("VAULT_DIR", str(_PROJECT_ROOT / "vault"))

# App-level KDF parameters. The Fernet key is derived deterministically from the
# user's chosen vault password, so the same password always yields the same key.
VAULT_SALT: bytes = b"my-ai-manager-secure-vault-salt"
VAULT_KDF_ITERATIONS: int = 100_000


def _derive_fernet_key(password: str) -> bytes:
    """Derive a Fernet-compatible key from a vault password via PBKDF2-HMAC-SHA256."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=VAULT_SALT,
        iterations=VAULT_KDF_ITERATIONS,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode("utf-8")))


@router.post("/upload", response_model=VaultFileOut, status_code=201)
def upload_vault_file(
    file: UploadFile = File(...),
    password: Annotated[str, Field(min_length=1, max_length=128)] = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Encrypt an uploaded file with a password-derived key and store it in the vault."""
    data = file.file.read()
    if not data:
        raise HTTPException(status_code=400, detail="File content is empty")

    encrypted = Fernet(_derive_fernet_key(password)).encrypt(data)

    record = VaultFile(
        user_id=current_user.id,
        filename=file.filename or "unnamed",
        encrypted_path="",
    )
    db.add(record)
    db.flush()

    target = Path(VAULT_DIR) / str(current_user.id) / f"{record.id}.enc"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(encrypted)
    record.encrypted_path = str(target)

    db.commit()
    db.refresh(record)
    return record


@router.get("/files", response_model=list[VaultFileOut])
def list_vault_files(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List the current user's vault files, newest first."""
    return (
        db.query(VaultFile)
        .filter(VaultFile.user_id == current_user.id)
        .order_by(VaultFile.created_at.desc())
        .all()
    )


@router.post("/download/{file_id}")
def download_vault_file(
    file_id: UUID,
    body: VaultDownloadRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Decrypt and return one of the current user's vault files using the vault password."""
    record = (
        db.query(VaultFile)
        .filter(VaultFile.id == file_id, VaultFile.user_id == current_user.id)
        .first()
    )
    if record is None:
        raise HTTPException(status_code=404, detail="Vault file not found")

    path = Path(record.encrypted_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Vault file is missing on disk")

    encrypted = path.read_bytes()
    try:
        decrypted = Fernet(_derive_fernet_key(body.password)).decrypt(encrypted)
    except InvalidToken:
        raise HTTPException(status_code=400, detail="Incorrect password")

    return Response(
        content=decrypted,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{record.filename}"'},
    )
