import { BudgetSummary } from '@/types/trip';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';

interface BudgetOverviewProps {
  budget: BudgetSummary;
}

export function BudgetOverview({ budget }: BudgetOverviewProps) {
  const percentageUsed = (budget.estimatedSpend / budget.totalBudget) * 100;
  const remaining = budget.totalBudget - budget.estimatedSpend;

  return (
    <Card className="bg-white border-slate-200 shadow-lg">
      <CardHeader>
        <CardTitle className="text-lg text-slate-900">Budget Overview</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-slate-600">Total Budget</span>
            <span className="font-semibold text-slate-900">
              {budget.totalBudget.toLocaleString()} {budget.currency}
            </span>
          </div>

          <div className="flex justify-between text-sm">
            <span className="text-slate-600">Estimated Spend</span>
            <span className="font-semibold text-sky-600">
              {budget.estimatedSpend.toLocaleString()} {budget.currency}
            </span>
          </div>

          <Progress value={percentageUsed} className="h-2" />

          <div className="flex justify-between text-sm">
            <span className="text-slate-600">Remaining</span>
            <span className={`font-semibold ${remaining >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {remaining.toLocaleString()} {budget.currency}
            </span>
          </div>
        </div>

        <div className="pt-4 border-t border-slate-200">
          <div className="flex justify-between text-sm">
            <span className="text-slate-600">Daily Average</span>
            <span className="font-medium text-slate-900">
              {budget.dailyAverage.toLocaleString()} {budget.currency}
            </span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
