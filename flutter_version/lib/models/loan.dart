double _toDouble(dynamic v) {
  if (v == null) return 0;
  if (v is num) return v.toDouble();
  return double.tryParse(v.toString()) ?? 0;
}

/// Reflète RepaymentSchema (ecole_nginx/app/Schemas/SVente.py:108-128).
class LoanRepaymentRecord {
  LoanRepaymentRecord({
    required this.id,
    required this.paidAmount,
    required this.loansId,
    this.paymentMethod,
    required this.createdAt,
  });

  factory LoanRepaymentRecord.fromJson(Map<String, dynamic> json) => LoanRepaymentRecord(
        id: json['id'].toString(),
        paidAmount: _toDouble(json['paid_amount']),
        loansId: json['loans_id']?.toString() ?? '',
        paymentMethod: json['payment_method']?.toString(),
        createdAt: json['created_at']?.toString() ?? '',
      );

  final String id;
  final double paidAmount;
  final String loansId;
  final String? paymentMethod;
  final String createdAt;
}

/// Reflète LoanSchema (ecole_nginx/app/Schemas/SVente.py:132-160) —
/// équivalent de loans_form()/sauvegarder_loans()/to_loans_repayments()
/// (school_client, Controllers/Main.py:4887-4972) : prêt accordé à un
/// Professeur/Personnel, avec son historique de remboursements.
class LoanRecord {
  LoanRecord({
    required this.id,
    required this.amount,
    required this.termMonths,
    required this.interestRate,
    required this.monthlyPayment,
    required this.remainingBalance,
    required this.status,
    this.user,
    required this.date,
    required this.repayments,
  });

  factory LoanRecord.fromJson(Map<String, dynamic> json) => LoanRecord(
        id: json['id'].toString(),
        amount: _toDouble(json['amount']),
        termMonths: (json['term_months'] as num?)?.toInt() ?? 0,
        interestRate: _toDouble(json['interest_rate']),
        monthlyPayment: _toDouble(json['monthly_payment']),
        remainingBalance: _toDouble(json['remaining_balance']),
        status: json['status']?.toString() ?? '',
        user: json['user']?.toString(),
        date: json['date']?.toString() ?? '',
        repayments: ((json['repayments'] as List?) ?? const [])
            .map((e) => LoanRepaymentRecord.fromJson(e as Map<String, dynamic>))
            .toList(),
      );

  final String id;
  final double amount;
  final int termMonths;
  final double interestRate;
  final double monthlyPayment;
  final double remainingBalance;
  final String status;
  final String? user;
  final String date;
  final List<LoanRepaymentRecord> repayments;
}

/// Reflète /v1/get-data-user-for-loans (RVente.py:259-296) : un
/// Professeur ou Personnel éligible à un prêt.
class LoanUserOption {
  LoanUserOption({required this.id, required this.nom, required this.prenom, required this.type});

  factory LoanUserOption.fromJson(Map<String, dynamic> json) => LoanUserOption(
        id: json['id'].toString(),
        nom: json['nom']?.toString() ?? '',
        prenom: json['prenom']?.toString() ?? '',
        type: json['type']?.toString() ?? '',
      );

  final String id;
  final String nom;
  final String prenom;
  final String type;

  String get fullName => '$nom $prenom';
}
