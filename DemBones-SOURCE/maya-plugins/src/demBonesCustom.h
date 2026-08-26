#ifndef __DEM_BONES_CUSTOM_H__
#define __DEM_BONES_CUSTOM_H__

#include <DemBones/DemBonesExt.h>

#include <maya/MComputation.h>

#include <sstream>
#include <iostream>
#include <iomanip>

class DemBonesCustom : public Dem::DemBonesExt<double, float>
{
public:
	double m_tolerance;
	double m_patience;

	DemBonesCustom() :
		m_tolerance(1e-3),
		m_patience(3)
	{
		nIters = 100;
		m_np = m_patience;
	}

	void showParameters()
	{
		std::stringstream ss;
		ss << "Parameters:\n";
		ss << "\tnBones (target)"	<< std::setw(20) << "= " << nB << "\n";
		ss << "\tnInitIters"		<< std::setw(20) << "= " << nInitIters << "\n";
		ss << "\tnIters"			<< std::setw(20) << "= " << nIters << "\n";
		ss << "\ttolerance"			<< std::setw(20) << "= " << m_tolerance << "\n";
		ss << "\tpatience"			<< std::setw(20) << "= " << m_patience << "\n";
		ss << "\tnTransIters"		<< std::setw(20) << "= " << nTransIters << "\n";
		ss << "\tnWeightsIters"		<< std::setw(20) << "= " << nWeightsIters << "\n";
		ss << "\tbindUpdate"		<< std::setw(20) << "= " << bindUpdate << "\n";

		ss << "\ttransAffine"		<< std::setw(20) << "= " << transAffine << "\n";
		ss << "\ttransAffineNorm"	<< std::setw(20) << "= " << transAffineNorm << "\n";
		ss << "\tnnz"				<< std::setw(20) << "= " << nnz << "\n";
		ss << "\tweightsSmooth"		<< std::setw(20) << "= " << weightsSmooth << "\n";
		ss << "\tweightsSmoothStep" << std::setw(20) << "= " << weightsSmoothStep << "\n";

		std::cout << ss.str() << std::endl;
	}

	void compute()
	{
		m_prevErr = -1.0;
		m_np = m_patience;
		m_computation.beginComputation();
		DemBonesExt<double, float>::compute();
	}

	void cbIterBegin()
	{
		std::cout << "  Iter #" << iter << ": ";
	}

	bool cbIterEnd()
	{
		double err = rmse();
		std::cout << "RMSE = " << err << std::endl;
		if ((err < m_prevErr*(1 + weightEps)) && ((m_prevErr - err) < m_tolerance * m_prevErr))
		{
			m_np--;
			if (m_np == 0)
			{
				std::cout << "Convergente is reached!\n";
				return true;
			}
			else
			{
				m_np = m_patience;
			}
		}
		m_prevErr = err;

		if (m_computation.isInterruptRequested())
		{
			m_computation.endComputation();
			return true;
		}
		return false;
	}

	void cbInitSplitBegin()
	{
		std::cout << ">";
	}

	void cbInitSplitEnd()
	{
		std::cout << nB;
	}

	void cbWeightsBegin()
	{
		std::cout << "Updating weights";
	}

	void cbWeightsEnd()
	{
		std::cout << " Done! ";
	}

	void cbTranformationsBegin()
	{
		std::cout << "Updating transformations";
	}

	void cbTransformationsEnd()
	{
		std::cout << " Done! ";
	}

	bool cbTransformationsIterEnd()
	{
		std::cout << ".";
		return false;
	}

	bool cbWeightsIterEnd()
	{
		std::cout << ".";
		return false;
	}

private:
	double m_prevErr;
	int m_np;

	MComputation m_computation;
};

#endif